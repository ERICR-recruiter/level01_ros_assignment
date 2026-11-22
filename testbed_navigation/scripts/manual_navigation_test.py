#!/usr/bin/env python3
"""Navigate using explicit Nav2 ComputePathToPose + FollowPath actions."""
import argparse
import math
import time

import rclpy
from action_msgs.msg import GoalStatus
from lifecycle_msgs.srv import GetState
from nav2_msgs.action import ComputePathToPose, FollowPath
from rclpy.action import ActionClient
from rclpy.parameter import Parameter


STATUS_NAMES = {
    GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED',
    GoalStatus.STATUS_ABORTED: 'ABORTED',
    GoalStatus.STATUS_CANCELED: 'CANCELED',
}


def wait_for_future(node, future, timeout, operation):
    rclpy.spin_until_future_complete(node, future, timeout_sec=timeout)
    if not future.done():
        raise TimeoutError(f'{operation} did not finish within {timeout}s')
    result = future.result()
    if result is None:
        raise RuntimeError(f'{operation} returned no result')
    return result


def check_active(node, name, timeout=12.0, attempts=3):
    """Verify lifecycle state without treating one delayed DDS response as failure.

    This is a bounded check: a genuinely unresponsive or inactive node still
    fails rather than allowing navigation to proceed with unknown state.
    """
    client = node.create_client(GetState, f'/{name}/get_state')
    last_problem = 'no response'
    try:
        for attempt in range(1, attempts + 1):
            if not client.wait_for_service(timeout_sec=timeout):
                last_problem = 'lifecycle service unavailable'
            else:
                future = client.call_async(GetState.Request())
                try:
                    response = wait_for_future(
                        node, future, timeout,
                        f'{name} lifecycle query (attempt {attempt}/{attempts})',
                    )
                except (TimeoutError, RuntimeError) as exc:
                    last_problem = str(exc)
                    # Avoid keeping a timed-out call pending in the client.
                    if hasattr(client, 'remove_pending_request'):
                        client.remove_pending_request(future)
                    else:
                        future.cancel()
                else:
                    state = response.current_state.label
                    if state == 'active':
                        return
                    last_problem = f'lifecycle state is {state!r}'
                    if state in ('inactive', 'unconfigured', 'finalized'):
                        raise RuntimeError(
                            f'{name} is {state}, not active; inspect Nav2 launch logs'
                        )

            if attempt < attempts:
                print(
                    f'WARNING: {name}: {last_problem}; '
                    f'retrying lifecycle check ({attempt}/{attempts})...',
                    flush=True,
                )
                time.sleep(1.0)

        raise RuntimeError(
            f'{name} lifecycle check failed after {attempts} attempts: '
            f'{last_problem}. Check /{name}/get_state, DDS, and Nav2 logs.'
        )
    finally:
        node.destroy_client(client)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('x', type=float)
    parser.add_argument('y', type=float)
    parser.add_argument('--yaw', type=float, default=0.0)
    parser.add_argument('--planning-timeout', type=float, default=60.0)
    parser.add_argument('--following-timeout', type=float, default=120.0)
    args = parser.parse_args()
    if args.planning_timeout <= 0 or args.following_timeout <= 0:
        parser.error('timeouts must be positive')

    rclpy.init()
    node = rclpy.create_node('manual_navigation_test', parameter_overrides=[
        Parameter('use_sim_time', Parameter.Type.BOOL, True),
    ])
    plan_handle = None
    follow_handle = None
    exit_code = 1
    try:
        # Action servers may be discoverable while their lifecycle nodes are inactive.
        check_active(node, 'planner_server')
        check_active(node, 'controller_server')
        print('Planner and controller lifecycle states: active', flush=True)

        planner = ActionClient(node, ComputePathToPose, '/compute_path_to_pose')
        controller = ActionClient(node, FollowPath, '/follow_path')
        if not planner.wait_for_server(timeout_sec=10.0):
            raise RuntimeError('ComputePathToPose action server unavailable')
        if not controller.wait_for_server(timeout_sec=10.0):
            raise RuntimeError('FollowPath action server unavailable')

        planning = ComputePathToPose.Goal()
        planning.goal.header.frame_id = 'map'
        planning.goal.header.stamp = node.get_clock().now().to_msg()
        planning.goal.pose.position.x = args.x
        planning.goal.pose.position.y = args.y
        planning.goal.pose.orientation.z = math.sin(args.yaw / 2)
        planning.goal.pose.orientation.w = math.cos(args.yaw / 2)
        planning.planner_id = 'GridBased'
        planning.use_start = False

        print(f'Computing path to ({args.x}, {args.y}), yaw={args.yaw}...', flush=True)
        plan_handle = wait_for_future(
            node, planner.send_goal_async(planning), 15.0, 'Planner goal acceptance')
        if not plan_handle.accepted:
            raise RuntimeError('Planner rejected the goal: check planner lifecycle and logs')

        try:
            plan_response = wait_for_future(
                node, plan_handle.get_result_async(), args.planning_timeout,
                'ComputePathToPose result')
        except TimeoutError:
            print('Planning timed out: requesting goal cancellation...', flush=True)
            wait_for_future(node, plan_handle.cancel_goal_async(), 10.0,
                            'Planner cancellation')
            raise

        if plan_response.status != GoalStatus.STATUS_SUCCEEDED:
            error_code = getattr(plan_response.result, 'error_code', 'unknown')
            raise RuntimeError(f'Planning failed: status={plan_response.status}, '
                               f'error_code={error_code}')
        path = plan_response.result.path
        if not path.poses:
            raise RuntimeError('Planner returned an empty path')

        endpoint = path.poses[-1].pose.position
        endpoint_error = math.hypot(endpoint.x - args.x, endpoint.y - args.y)
        print(f'Planning succeeded: {len(path.poses)} poses, '
              f'endpoint error={endpoint_error:.3f} m', flush=True)
        # NavFn may return a nearby reachable endpoint if tolerance is nonzero.
        if endpoint_error > 0.05:
            raise RuntimeError('Planner endpoint is >5cm from requested goal; '
                               'refusing to report nearby-point navigation as success')

        follow = FollowPath.Goal()
        follow.path = path
        follow.controller_id = 'FollowPath'
        follow.goal_checker_id = 'general_goal_checker'
        last_feedback = [0.0]

        def feedback_callback(message):
            now = time.monotonic()
            if now - last_feedback[0] >= 1.0:
                fb = message.feedback
                print(f'Distance: {fb.distance_to_goal:.3f} m | '
                      f'Speed: {fb.speed:.3f} m/s', flush=True)
                last_feedback[0] = now

        print('Following generated path...', flush=True)
        follow_handle = wait_for_future(
            node, controller.send_goal_async(follow, feedback_callback=feedback_callback),
            15.0, 'FollowPath goal acceptance')
        if not follow_handle.accepted:
            raise RuntimeError('Controller rejected the path')
        try:
            follow_response = wait_for_future(
                node, follow_handle.get_result_async(), args.following_timeout,
                'FollowPath result')
        except TimeoutError:
            print('FollowPath timed out: requesting cancellation...', flush=True)
            wait_for_future(node, follow_handle.cancel_goal_async(), 10.0,
                            'FollowPath cancellation')
            raise

        status_name = STATUS_NAMES.get(follow_response.status, str(follow_response.status))
        if follow_response.status != GoalStatus.STATUS_SUCCEEDED:
            code = getattr(follow_response.result, 'error_code', 'unknown')
            raise RuntimeError(f'Navigation {status_name}: error_code={code}')
        print('NAVIGATION SUCCEEDED (controller result; verify physical accuracy separately)',
              flush=True)
        exit_code = 0
    except (RuntimeError, TimeoutError) as exc:
        print(f'NAVIGATION FAILED: {exc}', flush=True)
    except KeyboardInterrupt:
        print('Interrupted: requesting cancellation of active action...', flush=True)
        active = follow_handle if follow_handle is not None and follow_handle.accepted \
            else plan_handle
        if active is not None and active.accepted:
            try:
                wait_for_future(node, active.cancel_goal_async(), 5.0,
                                'Action cancellation')
            except Exception as exc:
                print(f'Cancellation failed: {exc}', flush=True)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())

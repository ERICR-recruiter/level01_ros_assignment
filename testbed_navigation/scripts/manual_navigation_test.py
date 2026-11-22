#!/usr/bin/env python3
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.parameter import Parameter
from action_msgs.msg import GoalStatus
from nav2_msgs.action import ComputePathToPose, FollowPath
import argparse
import math

def main():
    rclpy.init()
    parser = argparse.ArgumentParser(
        description='Manually navigate the Testbed robot using Nav2 actions'
    )

    parser.add_argument('x', type=float, help='Goal X in map frame')
    parser.add_argument('y', type=float, help='Goal Y in map frame')
    parser.add_argument(
        '--yaw',
        type=float,
        default=0.0,
        help='Goal orientation in radians'
    )

    args = parser.parse_args()

    node = rclpy.create_node(
        'manual_navigation_test',
        parameter_overrides=[
            Parameter('use_sim_time', Parameter.Type.BOOL, True)
        ],
    )

    planner = ActionClient(
        node, ComputePathToPose, '/compute_path_to_pose'
    )
    controller = ActionClient(
        node, FollowPath, '/follow_path'
    )

    def get_future_result(future, timeout=60):
        rclpy.spin_until_future_complete(
            node, future, timeout_sec=timeout
        )
        if not future.done():
            raise TimeoutError('Action timed out')
        return future.result()

    try:
        print('Waiting for planner...')
        if not planner.wait_for_server(timeout_sec=10):
            raise RuntimeError('Planner action server unavailable')

        print('Waiting for controller...')
        if not controller.wait_for_server(timeout_sec=10):
            raise RuntimeError('Controller action server unavailable')

        # Step 1: Request path from current robot position
        planner_goal = ComputePathToPose.Goal()
        planner_goal.goal.header.frame_id = 'map'
        planner_goal.goal.header.stamp = node.get_clock().now().to_msg()
        planner_goal.goal.pose.position.x = args.x
        planner_goal.goal.pose.position.y = args.y
        planner_goal.goal.pose.orientation.w = math.cos(args.yaw/2.0)
        planner_goal.goal.pose.orientation.z = math.sin(args.yaw/2.0)
        planner_goal.planner_id = 'GridBased'
        planner_goal.use_start = False

        print(f'Computing path to ({args.x}, {args.y})...')

        plan_handle = get_future_result(
            planner.send_goal_async(planner_goal)
        )

        if not plan_handle.accepted:
            raise RuntimeError('Planner rejected the goal')

        plan_result = get_future_result(
            plan_handle.get_result_async()
        )

        if plan_result.status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError('Path planning failed')

        path = plan_result.result.path

        if not path.poses:
            raise RuntimeError('Planner returned an empty path')

        print(f'Planning succeeded: {len(path.poses)} poses')

        # Step 2: Send the actual planner path to the controller
        follow_goal = FollowPath.Goal()
        follow_goal.path = path
        follow_goal.controller_id = 'FollowPath'
        follow_goal.goal_checker_id = 'general_goal_checker'

        last_feedback = [0.0]

        def feedback_callback(message):
            now = time.monotonic()

            if now - last_feedback[0] >= 1.0:
                feedback = message.feedback
                print(
                    f'Distance: {feedback.distance_to_goal:.3f} m | '
                    f'Speed: {feedback.speed:.3f} m/s'
                )
                last_feedback[0] = now

        print('Following generated path...')

        follow_handle = get_future_result(
            controller.send_goal_async(
                follow_goal,
                feedback_callback=feedback_callback
            )
        )

        if not follow_handle.accepted:
            raise RuntimeError('Controller rejected the path')

        follow_future = follow_handle.get_result_async()

        rclpy.spin_until_future_complete(
            node, follow_future, timeout_sec=120
        )

        if not follow_future.done():
            print('Navigation timed out; cancelling goal...')
            get_future_result(
                follow_handle.cancel_goal_async(), timeout=10
            )
            raise TimeoutError('FollowPath timed out')

        result = follow_future.result()

        if result.status == GoalStatus.STATUS_SUCCEEDED:
            print('NAVIGATION SUCCEEDED')
        else:
            print(f'NAVIGATION FAILED: status={result.status}')

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
navigation_manager.py — Lightweight navigation coordinator for Testbed-T1.0.0

Provides a simple Python interface for:
  • Checking Nav2 action-server availability.
  • Sending navigation goals.
  • Monitoring navigation state.
  • Cancelling an in-progress goal.
  • Reporting clear status messages.

Usage:
    ros2 run testbed_navigation navigation_manager
    (interactive mode — enter goals from the terminal)
"""
import math
import sys
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Quaternion


def yaw_to_quaternion(yaw: float) -> Quaternion:
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class NavigationManager(Node):
    """Interactive navigation coordinator."""

    def __init__(self):
        super().__init__('navigation_manager')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._goal_handle = None
        self._navigating = False

    # ------------------------------------------------------------------ #
    #  Server readiness                                                  #
    # ------------------------------------------------------------------ #

    def wait_for_server(self, timeout_sec: float = 10.0) -> bool:
        self.get_logger().info('Waiting for navigate_to_pose server …')
        ready = self._client.wait_for_server(timeout_sec=timeout_sec)
        if ready:
            self.get_logger().info('Action server ready.')
        else:
            self.get_logger().error(
                f'Server not available after {timeout_sec} s'
            )
        return ready

    # ------------------------------------------------------------------ #
    #  Goal management                                                   #
    # ------------------------------------------------------------------ #

    def send_goal(self, x: float, y: float, yaw: float = 0.0):
        """Send a goal and block until the result is received."""
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation = yaw_to_quaternion(yaw)

        self.get_logger().info(
            f'→ Goal sent: x={x:.2f} y={y:.2f} yaw={yaw:.2f}'
        )
        self._navigating = True

        future = self._client.send_goal_async(
            goal, feedback_callback=self._feedback_cb
        )
        rclpy.spin_until_future_complete(self, future)
        self._goal_handle = future.result()

        if not self._goal_handle.accepted:
            self.get_logger().warn('Goal rejected.')
            self._navigating = False
            return False

        self.get_logger().info('Goal accepted — navigating …')
        result_future = self._goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self._navigating = False

        status = result_future.result().status
        success = status == 4  # SUCCEEDED
        label = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}.get(
            status, f'UNKNOWN({status})'
        )
        if success:
            self.get_logger().info(f'Result: {label} ✓')
        else:
            self.get_logger().warn(f'Result: {label}')
        return success

    def cancel(self):
        if self._goal_handle and self._navigating:
            self.get_logger().info('Cancelling …')
            self._goal_handle.cancel_goal_async()
            self._navigating = False

    # ------------------------------------------------------------------ #

    def _feedback_cb(self, msg):
        d = msg.feedback.distance_remaining
        self.get_logger().info(f'  distance remaining: {d:.2f} m')


# ---------------------------------------------------------------------- #
#  Interactive entry point                                                #
# ---------------------------------------------------------------------- #

def main(args=None):
    rclpy.init(args=args)
    mgr = NavigationManager()

    if not mgr.wait_for_server(timeout_sec=15.0):
        mgr.destroy_node()
        rclpy.shutdown()
        return

    print('\n--- Testbed Navigation Manager ---')
    print('Enter goals as:  x y [yaw]')
    print('Type "quit" or Ctrl-C to exit.\n')

    try:
        while rclpy.ok():
            line = input('goal> ').strip()
            if line.lower() in ('quit', 'exit', 'q'):
                break
            parts = line.split()
            if len(parts) < 2:
                print('Usage: x y [yaw]')
                continue
            try:
                x = float(parts[0])
                y = float(parts[1])
                yaw = float(parts[2]) if len(parts) > 2 else 0.0
            except ValueError:
                print('Invalid number.')
                continue
            mgr.send_goal(x, y, yaw)
    except (KeyboardInterrupt, EOFError):
        mgr.cancel()

    mgr.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
navigation_test.py — Automated smoke test for Testbed-T1.0.0 navigation

Sends a predefined goal within known free space and reports whether the
robot reached it.  Designed to be run after the full navigation stack is
active.

The test goal is at (1.0, 4.0) which is in verified free space on the
testbed_world map (the robot spawns at 0, 5).

Usage:
    ros2 run testbed_navigation navigation_test
"""
import math
import sys
import time
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


class NavigationTest(Node):

    # Test goal — verified free space on the testbed_world map
    GOAL_X = 1.0
    GOAL_Y = 4.0
    GOAL_YAW = 0.0
    TIMEOUT_SEC = 120.0

    def __init__(self):
        super().__init__('navigation_test')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._result_status = None
        self._last_feedback_log = 0.0

    def run_test(self) -> bool:
        self.get_logger().info('=== Navigation Smoke Test ===')
        self.get_logger().info(
            f'Goal: x={self.GOAL_X}, y={self.GOAL_Y}, yaw={self.GOAL_YAW}'
        )

        # Wait for server
        self.get_logger().info('Waiting for action server …')
        if not self._client.wait_for_server(timeout_sec=30.0):
            self.get_logger().error('Action server unavailable — FAIL')
            return False

        # Build goal
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = self.GOAL_X
        goal.pose.pose.position.y = self.GOAL_Y
        goal.pose.pose.orientation = yaw_to_quaternion(self.GOAL_YAW)

        # Send
        self.get_logger().info('Sending goal …')
        future = self._client.send_goal_async(
            goal, feedback_callback=self._feedback_cb
        )
        rclpy.spin_until_future_complete(self, future)
        handle = future.result()

        if not handle.accepted:
            self.get_logger().error('Goal rejected — FAIL')
            return False

        self.get_logger().info('Goal accepted — waiting for result …')
        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(
            self, result_future, timeout_sec=self.TIMEOUT_SEC
        )

        if not result_future.done():
            self.get_logger().error(
                f'Navigation timed out after {self.TIMEOUT_SEC} s — FAIL'
            )
            handle.cancel_goal_async()
            return False

        status = result_future.result().status
        success = status == 4  # GoalStatus.STATUS_SUCCEEDED
        if success:
            self.get_logger().info('=== PASS: Robot reached the goal ===')
        else:
            label = {5: 'CANCELED', 6: 'ABORTED'}.get(
                status, f'UNKNOWN({status})'
            )
            self.get_logger().error(f'=== FAIL: Navigation {label} ===')
        return success

    def _feedback_cb(self, msg):
        now = time.monotonic()
        if now - self._last_feedback_log >= 1.0:
            d = msg.feedback.distance_remaining
            self.get_logger().info(f'  remaining: {d:.2f} m')
            self._last_feedback_log = now


def main(args=None):
    rclpy.init(args=args)
    node = NavigationTest()
    success = node.run_test()
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

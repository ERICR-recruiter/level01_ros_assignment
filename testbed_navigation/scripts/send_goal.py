#!/usr/bin/env python3
"""Send a navigation goal to Nav2 bt_navigator via the NavigateToPose action.

Usage:
  ros2 run testbed_navigation send_goal.py --x 2.0 --y 4.0 --yaw 0.0
"""

import argparse
import math
import sys
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


class NavGoalClient(Node):

    def __init__(self):
        super().__init__('nav_goal_client')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, x: float, y: float, yaw: float = 0.0):
        self.get_logger().info('Waiting for NavigateToPose action server...')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('NavigateToPose action server not available!')
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Euler to Quaternion (yaw about Z)
        qz = math.sin(yaw / 2.0)
        qw = math.cos(yaw / 2.0)
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self.get_logger().info(f'Sending goal: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} rad')
        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_callback)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal was rejected by server!')
            return False

        self.get_logger().info('Goal accepted. Waiting for result...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        status = result_future.result().status
        self.get_logger().info(f'Navigation finished with status: {status}')
        return True

    def _feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'Remaining distance: {fb.distance_remaining:.2f} m',
            throttle_duration_sec=2.0)


def main(args=None):
    parser = argparse.ArgumentParser(description='Send Nav2 goal to Testbed robot')
    parser.add_argument('--x', type=float, default=2.0, help='Goal X coordinate (map frame)')
    parser.add_argument('--y', type=float, default=4.0, help='Goal Y coordinate (map frame)')
    parser.add_argument('--yaw', type=float, default=0.0, help='Goal Yaw in radians')
    parsed_args, _ = parser.parse_known_args()

    rclpy.init(args=args)
    client = NavGoalClient()
    success = client.send_goal(parsed_args.x, parsed_args.y, parsed_args.yaw)
    client.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

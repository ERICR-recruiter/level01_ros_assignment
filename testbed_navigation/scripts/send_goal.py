#!/usr/bin/env python3
import argparse
import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node


class GoalSender(Node):
    def __init__(self):
        super().__init__('goal_sender')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, x: float, y: float, yaw: float) -> None:
        self.get_logger().info('Waiting for navigate_to_pose action server...')
        self._client.wait_for_server()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info(f'Sending goal: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}')
        send_future = self._client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by action server')
            return

        self.get_logger().info('Goal accepted, waiting for result...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        status = result_future.result().status
        self.get_logger().info(f'Navigation finished with status code: {status}')


def main():
    parser = argparse.ArgumentParser(description='Send a NavigateToPose goal to Nav2')
    parser.add_argument('--x', type=float, default=2.0, help='Target X in map frame')
    parser.add_argument('--y', type=float, default=2.0, help='Target Y in map frame')
    parser.add_argument('--yaw', type=float, default=0.0, help='Target yaw in radians')
    args, _ = parser.parse_known_args()

    rclpy.init()
    node = GoalSender()
    try:
        node.send_goal(args.x, args.y, args.yaw)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

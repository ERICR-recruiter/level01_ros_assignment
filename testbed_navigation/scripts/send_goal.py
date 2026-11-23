#!/usr/bin/env python3
"""Send a NavigateToPose goal (map frame):  ros2 run testbed_navigation send_goal.py X Y [YAW_RAD]"""
import math
import sys

import rclpy
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node


class GoalSender(Node):
    def __init__(self):
        super().__init__('send_goal')
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send(self, x, y, yaw):
        self.client.wait_for_server()
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)
        self.get_logger().info(f'Sending goal x={x:.2f} y={y:.2f} yaw={yaw:.2f}')
        fut = self.client.send_goal_async(goal, feedback_callback=self.feedback)
        rclpy.spin_until_future_complete(self, fut)
        handle = fut.result()
        if not handle.accepted:
            self.get_logger().error('Goal rejected')
            return 1
        res = handle.get_result_async()
        rclpy.spin_until_future_complete(self, res)
        status = res.result().status  # 4 == SUCCEEDED
        self.get_logger().info('Goal succeeded' if status == 4 else f'Goal ended with status {status}')
        return 0 if status == 4 else 1

    def feedback(self, msg):
        self.get_logger().info(
            f'distance remaining: {msg.feedback.distance_remaining:.2f} m', throttle_duration_sec=2.0)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    x, y = float(sys.argv[1]), float(sys.argv[2])
    yaw = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    rclpy.init()
    node = GoalSender()
    code = node.send(x, y, yaw)
    node.destroy_node()
    rclpy.shutdown()
    return code


if __name__ == '__main__':
    sys.exit(main())

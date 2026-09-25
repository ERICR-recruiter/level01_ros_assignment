#!/usr/bin/env python3

import argparse
import math
import sys

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node


class GoalSender(Node):

    def __init__(self):
        super().__init__('send_goal')
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send(self, x, y, yaw, frame):
        if not self.client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('navigate_to_pose action server is not up')
            return 1

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = frame
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info(
            'sending goal x=%.2f y=%.2f yaw=%.2f in %s' % (x, y, yaw, frame))

        send_future = self.client.send_goal_async(goal, self.on_feedback)
        rclpy.spin_until_future_complete(self, send_future)
        handle = send_future.result()
        if not handle.accepted:
            self.get_logger().error('goal was rejected')
            return 1

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        status = result_future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('goal reached')
            return 0

        self.get_logger().error('navigation ended with status %d' % status)
        return 1

    def on_feedback(self, msg):
        fb = msg.feedback
        self.get_logger().info(
            'remaining %.2f m, %d recoveries' % (fb.distance_remaining,
                                                 fb.number_of_recoveries),
            throttle_duration_sec=2.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('x', type=float)
    parser.add_argument('y', type=float)
    parser.add_argument('yaw', type=float, nargs='?', default=0.0)
    parser.add_argument('--frame', default='map')
    args = parser.parse_args()

    rclpy.init()
    node = GoalSender()
    try:
        code = node.send(args.x, args.y, args.yaw, args.frame)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return code


if __name__ == '__main__':
    sys.exit(main())

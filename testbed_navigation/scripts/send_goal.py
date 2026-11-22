#!/usr/bin/env python3
"""Simple CLI helper to send a NavigateToPose goal to Nav2 for testing."""

import argparse
import math
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose


class GoalSender(Node):
    def __init__(self):
        super().__init__("testbed_goal_sender")
        self._client = ActionClient(self, NavigateToPose, "navigate_to_pose")

    def send_goal(self, x: float, y: float, yaw: float) -> bool:
        self.get_logger().info("Waiting for navigate_to_pose action server...")
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("navigate_to_pose action server not available.")
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        # Leave stamp at (0, 0) so TF resolves the latest transform without sim/wall clock skew
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info(
            f"Sending goal: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} rad"
        )
        send_future = self._client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_cb
        )
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("Goal was rejected by bt_navigator.")
            return False

        self.get_logger().info("Goal accepted. Navigating...")
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        status = result_future.result().status
        self.get_logger().info(f"Navigation finished with action status code: {status}")
        return True

    def _feedback_cb(self, feedback_msg):
        dist = feedback_msg.feedback.distance_remaining
        self.get_logger().info(
            f"Distance remaining: {dist:.2f} m", throttle_duration_sec=2.0
        )


def main():
    parser = argparse.ArgumentParser(description="Send a 2D Nav2 goal pose.")
    parser.add_argument("--x", type=float, required=True, help="Target X in map frame (m)")
    parser.add_argument("--y", type=float, required=True, help="Target Y in map frame (m)")
    parser.add_argument("--yaw", type=float, default=0.0, help="Target yaw in radians")
    args, ros_args = parser.parse_known_args()

    rclpy.init(args=ros_args)
    node = GoalSender()
    try:
        ok = node.send_goal(args.x, args.y, args.yaw)
    finally:
        node.destroy_node()
        rclpy.shutdown()

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

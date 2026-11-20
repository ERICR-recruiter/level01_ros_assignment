#!/usr/bin/env python3
"""Send a NavigateToPose goal to bt_navigator from the command line.

    ros2 run testbed_navigation send_goal.py 3.0 -5.0 1.57      # x y [yaw]
"""
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
        super().__init__('testbed_goal_sender')
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._last_log = 0.0

    def send(self, x, y, yaw):
        self.get_logger().info('Waiting for navigate_to_pose action server...')
        self.client.wait_for_server()

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info(f'Sending goal x={x:.2f} y={y:.2f} yaw={yaw:.2f}')
        send_future = self.client.send_goal_async(goal, feedback_callback=self._feedback)
        rclpy.spin_until_future_complete(self, send_future)
        handle = send_future.result()
        if not handle.accepted:
            self.get_logger().error('Goal rejected')
            return False

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        status = result_future.result().status
        ok = status == GoalStatus.STATUS_SUCCEEDED
        (self.get_logger().info if ok else self.get_logger().error)(
            'Goal SUCCEEDED' if ok else f'Goal finished with status {status}')
        return ok

    def _feedback(self, msg):
        fb = msg.feedback
        now = self.get_clock().now().nanoseconds * 1e-9
        if now - self._last_log > 2.0:
            self._last_log = now
            p = fb.current_pose.pose.position
            self.get_logger().info(
                f'at ({p.x:.2f}, {p.y:.2f})  distance remaining {fb.distance_remaining:.2f} m  '
                f'recoveries {fb.number_of_recoveries}')


def main():
    args = [a for a in rclpy.utilities.remove_ros_args(sys.argv)[1:]]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    x, y = float(args[0]), float(args[1])
    yaw = float(args[2]) if len(args) > 2 else 0.0
    rclpy.init()
    node = GoalSender()
    ok = node.send(x, y, yaw)
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

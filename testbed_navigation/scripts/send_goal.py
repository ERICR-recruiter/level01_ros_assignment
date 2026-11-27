#!/usr/bin/env python3
"""Send one or more goals to the nav2 `navigate_to_pose` action server.

This is the "manual" way of calling the NavigateToPose action that
bt_navigator exposes (what the RViz "Nav2 Goal" button does internally).

    ros2 run testbed_navigation send_goal.py --x 5.0 --y 5.0 --yaw 0.0
    # several goals in sequence: x,y,yaw triplets
    ros2 run testbed_navigation send_goal.py --waypoints "5,5,0  5,-2,-1.57  0,5,3.14"
"""

import argparse
import math
import sys

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node


def make_pose(node, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = node.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    # yaw -> quaternion (rotation about z only)
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


class GoalSender(Node):

    def __init__(self):
        super().__init__('testbed_goal_sender')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def go_to(self, x, y, yaw):
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("'navigate_to_pose' action server not available. "
                                    'Is navigation.launch.py running?')
            return False

        goal = NavigateToPose.Goal()
        goal.pose = make_pose(self, x, y, yaw)
        self.get_logger().info(f'Sending goal x={x:.2f} y={y:.2f} yaw={yaw:.2f}')

        send_future = self._client.send_goal_async(goal, feedback_callback=self._feedback)
        rclpy.spin_until_future_complete(self, send_future)
        handle = send_future.result()
        if not handle.accepted:
            self.get_logger().error('Goal rejected')
            return False

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        status = result_future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Goal reached')
            return True
        self.get_logger().error(f'Goal finished with status {status}')
        return False

    def _feedback(self, msg):
        fb = msg.feedback
        self.get_logger().info(
            f'distance remaining: {fb.distance_remaining:.2f} m, '
            f'recoveries: {fb.number_of_recoveries}',
            throttle_duration_sec=2.0)


def parse_waypoints(text):
    waypoints = []
    for triplet in text.split():
        x, y, yaw = (float(v) for v in triplet.split(','))
        waypoints.append((x, y, yaw))
    return waypoints


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--x', type=float, default=5.0)
    parser.add_argument('--y', type=float, default=5.0)
    parser.add_argument('--yaw', type=float, default=0.0, help='radians')
    parser.add_argument('--waypoints', type=str, default='',
                        help='space separated "x,y,yaw" triplets, visited in order')
    args = parser.parse_args(rclpy.utilities.remove_ros_args(sys.argv)[1:])

    rclpy.init()
    node = GoalSender()
    goals = parse_waypoints(args.waypoints) if args.waypoints else [(args.x, args.y, args.yaw)]
    ok = True
    for x, y, yaw in goals:
        ok = node.go_to(x, y, yaw) and ok
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

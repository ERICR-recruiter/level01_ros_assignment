#!/usr/bin/env python3
"""Send one nav goal: send_goal.py --x 6 --y 7.5 --yaw 0"""
import argparse
import math
import sys

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def make_pose(nav, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--x', type=float, required=True)
    parser.add_argument('--y', type=float, required=True)
    parser.add_argument('--yaw', type=float, default=0.0, help='radians')
    args, ros_args = parser.parse_known_args()

    rclpy.init(args=ros_args)
    nav = BasicNavigator()
    nav.waitUntilNav2Active(localizer='amcl')

    nav.goToPose(make_pose(nav, args.x, args.y, args.yaw))
    while not nav.isTaskComplete():
        fb = nav.getFeedback()
        if fb:
            nav.get_logger().info(
                f'distance remaining: {fb.distance_remaining:.2f} m', throttle_duration_sec=2.0)

    result = nav.getResult()
    ok = result == TaskResult.SUCCEEDED
    nav.get_logger().info(f'Result: {result.name if hasattr(result, "name") else result}')
    nav.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

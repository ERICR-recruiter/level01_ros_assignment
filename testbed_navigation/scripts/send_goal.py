#!/usr/bin/env python3

import math
import rclpy

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def make_pose(navigator, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose

def main():
    rclpy.init()
    navigator = BasicNavigator()

    navigator.setInitialPose(make_pose(navigator, 0.0, 5.0, 0.0))
    navigator.waitUntilNav2Active()

    goal = make_pose(navigator, 6.84, 5.39, 3.05)   # replace with a free-space point
    navigator.goToPose(goal)

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            print(f'distance remaining: {feedback.distance_remaining:.2f} m')

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Goal reached')
    elif result == TaskResult.CANCELED:
        print('Goal canceled')
    else:
        print('Goal failed')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
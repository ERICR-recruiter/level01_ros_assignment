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

    # three poses you already drove to successfully
    waypoints = [
        make_pose(navigator, 6.84, 5.39, 3.05),
        make_pose(navigator, -6.89, 1.18, -1.55),
        make_pose(navigator, 0.0, 5.0, 0.0),      # back to start
    ]

    start = navigator.get_clock().now()
    navigator.followWaypoints(waypoints)

    last_wp = -1
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback and feedback.current_waypoint != last_wp:
            last_wp = feedback.current_waypoint
            print(f'executing waypoint {last_wp + 1}/{len(waypoints)}')

    elapsed = (navigator.get_clock().now() - start).nanoseconds / 1e9
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print(f'Patrol finished in {elapsed:.1f} s (sim time)')
    elif result == TaskResult.CANCELED:
        print('Patrol canceled')
    else:
        print('Patrol failed')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
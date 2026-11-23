#!/usr/bin/env python3
"""Send one or more NavigateToPose goals to the testbed and report the result.

    # single goal  (x y yaw[rad], map frame)
    ros2 run testbed_navigation send_goal.py 5.0 5.0 0.0

    # built-in demo tour through the rooms of the test world
    ros2 run testbed_navigation send_goal.py --tour
"""
import math
import sys

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

# (x, y, yaw) waypoints in the map frame - each is in free space of testbed_world
DEMO_TOUR = [
    (5.0, 5.0, 0.0),       # north-east room
    (3.7, -3.0, -1.57),    # through the east doorway into the south half
    (-6.7, -3.0, 3.14),    # south-west
    (-6.7, 3.0, 1.57),     # back north through the west doorway
    (0.0, 5.0, 0.0),       # return to the spawn pose
]


def make_pose(nav, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--ros-args')]
    if '--tour' in args:
        goals = DEMO_TOUR
    elif len(args) >= 2:
        goals = [(float(args[0]), float(args[1]), float(args[2]) if len(args) > 2 else 0.0)]
    else:
        print(__doc__)
        return 1

    rclpy.init()
    nav = BasicNavigator()
    # AMCL gets its initial pose from amcl_params.yaml, so only wait for
    # bt_navigator to be active (do not wait for an /initialpose message).
    nav.waitUntilNav2Active(navigator='bt_navigator', localizer='amcl')

    ok = True
    for i, (x, y, yaw) in enumerate(goals, 1):
        nav.get_logger().info(f'[{i}/{len(goals)}] goal -> x={x:.2f} y={y:.2f} yaw={yaw:.2f}')
        nav.goToPose(make_pose(nav, x, y, yaw))
        while not nav.isTaskComplete():
            fb = nav.getFeedback()
            if fb:
                nav.get_logger().info(
                    f'    distance remaining: {fb.distance_remaining:.2f} m',
                    throttle_duration_sec=2.0)
        result = nav.getResult()
        if result == TaskResult.SUCCEEDED:
            nav.get_logger().info('    goal reached')
        else:
            nav.get_logger().error(f'    goal finished with {result}')
            ok = False
            break

    nav.destroy_node()
    rclpy.shutdown()
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())

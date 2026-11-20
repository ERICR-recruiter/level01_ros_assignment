#!/usr/bin/env python3
"""Send NavigateToPose goals in order and print status, time and final pose.

Usage: ros2 run testbed_navigation send_goals.py x,y,yaw_deg [x,y,yaw_deg ...]
       (default: a short demo route)
"""
import math
import sys

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter import Parameter

DEFAULT_GOALS = [(1.5, 6.5, 90.0), (3.7, -2.5, -90.0), (-9.0, -9.0, 180.0), (0.0, 5.0, 0.0)]
STATUS = {GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED', GoalStatus.STATUS_ABORTED: 'ABORTED',
          GoalStatus.STATUS_CANCELED: 'CANCELED'}


def make_pose(node, x, y, yaw_deg):
    p = PoseStamped()
    p.header.frame_id = 'map'
    p.header.stamp = node.get_clock().now().to_msg()
    p.pose.position.x, p.pose.position.y = x, y
    p.pose.orientation.z = math.sin(math.radians(yaw_deg) / 2)
    p.pose.orientation.w = math.cos(math.radians(yaw_deg) / 2)
    return p


def main():
    goals = [tuple(map(float, a.split(','))) for a in sys.argv[1:] if ',' in a] or DEFAULT_GOALS
    rclpy.init()
    node = Node('send_goals', parameter_overrides=[Parameter('use_sim_time', value=True)])
    client = ActionClient(node, NavigateToPose, 'navigate_to_pose')
    client.wait_for_server()
    while node.get_clock().now().nanoseconds == 0:  # wait for the first /clock message
        rclpy.spin_once(node, timeout_sec=0.1)
    for i, (x, y, yaw) in enumerate(goals, 1):
        goal = NavigateToPose.Goal(pose=make_pose(node, x, y, yaw))
        last = {}
        send = client.send_goal_async(goal, feedback_callback=lambda f: last.update(fb=f.feedback))
        rclpy.spin_until_future_complete(node, send)
        handle = send.result()
        if not handle.accepted:
            print(f'G{i} ({x}, {y}, {yaw}): REJECTED')
            continue
        start = node.get_clock().now()
        res = handle.get_result_async()
        rclpy.spin_until_future_complete(node, res)
        secs = (node.get_clock().now() - start).nanoseconds / 1e9
        fb = last.get('fb')
        pose = fb.current_pose.pose if fb else None
        where = (f'({pose.position.x:.3f}, {pose.position.y:.3f})' if pose else 'n/a')
        recov = fb.number_of_recoveries if fb else 'n/a'
        print(f'G{i} ({x}, {y}, {yaw}): {STATUS.get(res.result().status, res.result().status)} '
              f'in {secs:.1f} s (sim), final pose {where}, recoveries {recov}', flush=True)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

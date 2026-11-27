#!/usr/bin/env python3
"""
Send test navigation goals to the Testbed-T1.0.0 through Nav2 (nav2_simple_commander).

Requires the simulation, map_loader, localization and navigation launch files to be running
(or bringup_all.launch.py).

Usage:
  ros2 run testbed_navigation send_goals.py                     # tour of the whole map
  ros2 run testbed_navigation send_goals.py --goal 6.0 6.0 0.0  # single goal: x y yaw[rad]
  ros2 run testbed_navigation send_goals.py --spawn-obstacle    # drop an unmapped box on leg 1
  ros2 run testbed_navigation send_goals.py --set-initial-pose  # re-seed AMCL at the spawn pose

Goals are taken from testbed_world.pgm: each has >= 0.85 m clearance to the nearest occupied
cell, and each leg is traversable with >= 0.22 m clearance (the tour uses both top/bottom
doorways, at x ~ 3.7 and x ~ -6.7).
"""

import argparse
import math
import sys

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration
from rclpy.parameter import Parameter
from rclpy.utilities import remove_ros_args

# Robot spawn pose in testbed_gazebo/launch/spawn_testbed.launch.py (map frame ~= Gazebo world).
SPAWN_POSE = (0.0, 5.0, 0.0)

# (name, x, y, yaw) in the map frame. Clearance = distance to the nearest non-free map cell.
TOUR = [
    ('top-right room', 6.0, 6.0, 0.0),                # clearance 3.80 m
    ('bottom-right pocket, past the box', 8.8, -8.8, -math.pi / 2),  # 0.85 m; via the doorway
    ('bottom-left room', -6.0, -6.0, math.pi),        # 1.85 m; through the x=-3.2 wall gap
    ('top-left room', -6.5, 3.6, math.pi / 2),        # 3.50 m
    ('home (spawn pose)', 0.0, 5.0, 0.0),             # 3.35 m
]

# Unmapped obstacle for --spawn-obstacle: placed on the straight line from the spawn pose to
# the first tour goal; only the costmap obstacle layers (fed by /scan) can see it.
OBSTACLE_NAME = 'unmapped_box'
OBSTACLE_XY = (3.0, 5.5)
OBSTACLE_SDF = """<?xml version="1.0"?>
<sdf version="1.6">
  <model name="unmapped_box">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <geometry><box><size>0.4 0.4 0.5</size></box></geometry>
      </collision>
      <visual name="visual">
        <geometry><box><size>0.4 0.4 0.5</size></box></geometry>
        <material>
          <script>
            <uri>file://media/materials/scripts/gazebo.material</uri>
            <name>Gazebo/Red</name>
          </script>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

GOAL_TIMEOUT_S = 240.0


def make_pose(navigator, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def wait_for_amcl_pose(navigator):
    """
    Block until AMCL has published /amcl_pose (transient local, so a late join works).

    Humble's BasicNavigator.waitUntilNav2Active() publishes navigator.initial_pose, which
    defaults to (0, 0), whenever it has not yet seen /amcl_pose; that would reset AMCL away
    from the real spawn pose (0, 5). Waiting first sets initial_pose_received, so
    waitUntilNav2Active() never publishes the default.
    """
    waited = 0.0
    while rclpy.ok() and not navigator.initial_pose_received:
        if waited % 5.0 == 0.0:
            navigator.info('Waiting for /amcl_pose (is localization.launch.py running?)')
        rclpy.spin_once(navigator, timeout_sec=1.0)
        waited += 1.0


def spawn_obstacle(navigator):
    from gazebo_msgs.srv import SpawnEntity

    client = navigator.create_client(SpawnEntity, '/spawn_entity')
    if not client.wait_for_service(timeout_sec=5.0):
        navigator.warn('/spawn_entity not available; is Gazebo running? Skipping obstacle.')
        return
    request = SpawnEntity.Request()
    request.name = OBSTACLE_NAME
    request.xml = OBSTACLE_SDF
    request.reference_frame = 'world'
    request.initial_pose.position.x = OBSTACLE_XY[0]
    request.initial_pose.position.y = OBSTACLE_XY[1]
    request.initial_pose.position.z = 0.25
    future = client.call_async(request)
    rclpy.spin_until_future_complete(navigator, future, timeout_sec=10.0)
    response = future.result()
    if response is not None and response.success:
        navigator.info(f'Spawned {OBSTACLE_NAME} at {OBSTACLE_XY} (not in the static map)')
    else:
        message = response.status_message if response is not None else 'timeout'
        navigator.warn(f'Could not spawn {OBSTACLE_NAME}: {message}')


def navigate(navigator, name, x, y, yaw):
    navigator.info(f'Goal "{name}": x={x:.2f} y={y:.2f} yaw={yaw:.2f}')
    if not navigator.goToPose(make_pose(navigator, x, y, yaw)):
        return TaskResult.FAILED

    ticks = 0
    while not navigator.isTaskComplete():
        ticks += 1
        feedback = navigator.getFeedback()
        if feedback is None or ticks % 10:
            continue
        elapsed = Duration.from_msg(feedback.navigation_time).nanoseconds / 1e9
        eta = Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9
        print(f'  remaining {feedback.distance_remaining:5.2f} m | ETA {eta:5.1f} s | '
              f'elapsed {elapsed:5.1f} s | recoveries {feedback.number_of_recoveries}')
        if elapsed > GOAL_TIMEOUT_S:
            navigator.warn(f'Goal "{name}" exceeded {GOAL_TIMEOUT_S:.0f} s; cancelling')
            navigator.cancelTask()

    return navigator.getResult()


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--goal', nargs=3, type=float, metavar=('X', 'Y', 'YAW'),
                        help='send one goal in the map frame instead of the tour')
    parser.add_argument('--set-initial-pose', action='store_true',
                        help=f'publish /initialpose at the spawn pose {SPAWN_POSE} first')
    parser.add_argument('--spawn-obstacle', action='store_true',
                        help=f'spawn an unmapped box at {OBSTACLE_XY} in Gazebo first')
    return parser.parse_args(argv)


def main():
    args = parse_args(remove_ros_args(sys.argv)[1:])
    rclpy.init(args=sys.argv)

    navigator = BasicNavigator()
    # Stamp goals with the Gazebo clock, like every other node in this stack.
    navigator.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])

    if args.set_initial_pose:
        navigator.setInitialPose(make_pose(navigator, *SPAWN_POSE))
    else:
        wait_for_amcl_pose(navigator)
    navigator.waitUntilNav2Active(localizer='amcl')

    if args.spawn_obstacle:
        spawn_obstacle(navigator)

    goals = [('single goal', *args.goal)] if args.goal else TOUR
    results = []
    for name, x, y, yaw in goals:
        result = navigate(navigator, name, x, y, yaw)
        results.append((name, result))
        navigator.info(f'Goal "{name}": {result.name}')

    print('\nSummary')
    for name, result in results:
        print(f'  {result.name:9s} {name}')

    navigator.destroy_node()
    rclpy.shutdown()
    return 0 if all(r == TaskResult.SUCCEEDED for _, r in results) else 1


if __name__ == '__main__':
    sys.exit(main())

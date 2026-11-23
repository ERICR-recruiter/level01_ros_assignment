#!/usr/bin/env python3
"""Bring up the Nav2 navigation servers one by one (no nav2_bringup).

  planner_server      global planner (NavFn) + global costmap
  controller_server   local planner (DWB)    + local costmap  -> publishes /cmd_vel
  behavior_server     recovery behaviours (spin / backup / wait)
  bt_navigator        behaviour-tree executor, exposes /navigate_to_pose
  waypoint_follower   /follow_waypoints
  lifecycle_manager   configures + activates all of the above

Needs map_loader.launch.py and localization.launch.py to be running.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_args = [
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_nav, 'config', 'nav2_params.yaml'),
            description='Nav2 parameter file'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo clock'),
    ]

    common = dict(output='screen',
                  parameters=[params_file, {'use_sim_time': use_sim_time}])

    controller_server = Node(
        package='nav2_controller', executable='controller_server',
        name='controller_server', **common)

    planner_server = Node(
        package='nav2_planner', executable='planner_server',
        name='planner_server', **common)

    behavior_server = Node(
        package='nav2_behaviors', executable='behavior_server',
        name='behavior_server', **common)

    bt_navigator = Node(
        package='nav2_bt_navigator', executable='bt_navigator',
        name='bt_navigator', **common)

    waypoint_follower = Node(
        package='nav2_waypoint_follower', executable='waypoint_follower',
        name='waypoint_follower', **common)

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['controller_server',
                                    'planner_server',
                                    'behavior_server',
                                    'bt_navigator',
                                    'waypoint_follower']}],
    )

    return LaunchDescription(declare_args + [
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        waypoint_follower,
        lifecycle_manager,
    ])

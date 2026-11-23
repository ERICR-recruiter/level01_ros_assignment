#!/usr/bin/env python3
"""Bring up the Nav2 navigation servers by hand (no nav2_bringup).

Starts:
  * controller_server   - local planner (DWB) + local costmap, publishes /cmd_vel
  * planner_server      - global planner (NavFn) + global costmap
  * behavior_server     - recovery behaviours (spin, backup, wait, drive_on_heading)
  * bt_navigator        - behaviour tree that exposes the NavigateToPose action
  * lifecycle_manager_navigation - configures + activates the four nodes above

map_loader.launch.py and localization.launch.py must already be running.

Usage:
  ros2 launch testbed_navigation navigation.launch.py
Then send a goal with the "Nav2 Goal" tool in RViz, or from a terminal:
  ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
    "{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 5.0}, orientation: {w: 1.0}}}}"
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_args = [
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_pkg, 'config', 'nav2_params.yaml'),
            description='Parameter file for the Nav2 servers'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically configure and activate the Nav2 servers'),
    ]

    common = {'output': 'screen', 'respawn': False}
    params = [params_file, {'use_sim_time': use_sim_time}]

    controller_server = Node(
        package='nav2_controller', executable='controller_server',
        name='controller_server', parameters=params, **common)

    planner_server = Node(
        package='nav2_planner', executable='planner_server',
        name='planner_server', parameters=params, **common)

    behavior_server = Node(
        package='nav2_behaviors', executable='behavior_server',
        name='behavior_server', parameters=params, **common)

    bt_navigator = Node(
        package='nav2_bt_navigator', executable='bt_navigator',
        name='bt_navigator', parameters=params, **common)

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            # bring-up order matters: servers first, bt_navigator last
            'node_names': ['controller_server', 'planner_server',
                           'behavior_server', 'bt_navigator'],
        }],
    )

    return LaunchDescription(
        declare_args + [controller_server, planner_server, behavior_server,
                        bt_navigator, lifecycle_manager])

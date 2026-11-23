#!/usr/bin/env python3
"""Localize the robot on the loaded map with nav2_amcl.

Starts two nodes:
  * amcl                          - lifecycle node, publishes the map -> odom transform
  * lifecycle_manager_localization - configures + activates amcl (autostart)

map_loader.launch.py must be running (AMCL needs the /map topic).

Usage:
  ros2 launch testbed_navigation localization.launch.py
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
            default_value=os.path.join(nav_pkg, 'config', 'amcl_params.yaml'),
            description='Parameter file for amcl'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically configure and activate amcl'),
    ]

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': ['amcl'],
        }],
    )

    return LaunchDescription(declare_args + [amcl, lifecycle_manager])

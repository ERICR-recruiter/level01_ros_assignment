#!/usr/bin/env python3
"""Load the provided occupancy-grid map with nav2_map_server.

map_server is a lifecycle node, so a dedicated lifecycle_manager configures
and activates it. The map is then published (latched) on /map.

Usage:
  ros2 launch testbed_navigation map_loader.launch.py
  ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/to/other.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('testbed_navigation')
    pkg_bringup = get_package_share_directory('testbed_bringup')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_args = [
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(pkg_bringup, 'maps', 'testbed_world.yaml'),
            description='Absolute path to the map yaml file'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_nav, 'config', 'map_server_params.yaml'),
            description='map_server parameter file'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo clock'),
    ]

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[params_file,
                    {'yaml_filename': map_yaml, 'use_sim_time': use_sim_time}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['map_server']}],
    )

    return LaunchDescription(declare_args + [map_server, lifecycle_manager])

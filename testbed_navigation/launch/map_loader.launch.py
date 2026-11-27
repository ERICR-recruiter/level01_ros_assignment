#!/usr/bin/env python3
"""Load the Testbed map with nav2_map_server, started through its lifecycle manager."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('testbed_bringup')
    nav_dir = get_package_share_directory('testbed_navigation')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_dir, 'maps', 'testbed_world.yaml'),
            description='Full path to the map YAML file'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'map_server_params.yaml'),
            description='Full path to the map_server parameter file'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo simulation clock'),
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[params_file, {
                'yaml_filename': map_yaml,
                'use_sim_time': use_sim_time,
            }]),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map_server',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': ['map_server'],
            }]),
    ])

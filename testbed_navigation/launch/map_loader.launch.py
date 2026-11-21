#!/usr/bin/env python3
"""Loads the static map using nav2_map_server and activates it with a lifecycle manager."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml,
            'use_sim_time': use_sim_time,
            'topic_name': 'map',
            'frame_id': 'map',
        }],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': ['map_server'],
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Full path to the map yaml file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use Gazebo /clock'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Automatically configure and activate map_server'),
        map_server,
        lifecycle_manager,
    ])

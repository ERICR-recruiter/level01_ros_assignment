#!/usr/bin/env python3
"""Load the testbed map with nav2_map_server (managed by its own lifecycle manager)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            os.path.join(nav_dir, 'config', 'map_server_params.yaml'),
            {'yaml_filename': map_yaml, 'use_sim_time': use_sim_time},
        ],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server'],
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo clock'),
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Absolute path to the map yaml'),
        map_server,
        lifecycle_manager,
    ])

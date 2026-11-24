#!/usr/bin/env python3
"""Load the testbed map with nav2_map_server (lifecycle node + lifecycle manager)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')
    bringup_pkg = get_package_share_directory('testbed_bringup')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('map_params_file')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[params_file,
                    {'use_sim_time': use_sim_time, 'yaml_filename': map_yaml}],
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

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_pkg, 'maps', 'testbed_world.yaml'),
            description='Full path to the map yaml file'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock'),
        DeclareLaunchArgument(
            'map_params_file',
            default_value=os.path.join(nav_pkg, 'config', 'map_server_params.yaml'),
            description='map_server parameter file'),
        map_server,
        lifecycle_manager,
    ])

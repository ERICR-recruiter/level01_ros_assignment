#!/usr/bin/env python3
"""Step 1 - Map loading.

Starts nav2_map_server (a lifecycle node) with the testbed map and a dedicated
lifecycle manager that configures + activates it. The map is published latched
(transient local) on /map in the `map` frame.

    ros2 launch testbed_navigation map_loader.launch.py
    ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/other_map.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')
    bringup_share = get_package_share_directory('testbed_bringup')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('map_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    declare_args = [
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_share, 'maps', 'testbed_world.yaml'),
            description='Absolute path to the map yaml file'),
        DeclareLaunchArgument(
            'map_params_file',
            default_value=os.path.join(nav_share, 'config', 'map_server_params.yaml'),
            description='map_server parameter file'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically configure + activate the map server'),
        DeclareLaunchArgument('log_level', default_value='info'),
    ]

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[params_file,
                    {'yaml_filename': map_yaml, 'use_sim_time': use_sim_time}],
        arguments=['--ros-args', '--log-level', log_level],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': autostart,
                     'node_names': ['map_server']}],
    )

    return LaunchDescription(declare_args + [map_server, lifecycle_manager])

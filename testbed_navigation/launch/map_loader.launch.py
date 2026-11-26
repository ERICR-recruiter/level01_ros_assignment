#!/usr/bin/env python3
"""
map_loader.launch.py — Start Nav2 Map Server for Testbed-T1.0.0

Loads the pre-built map from testbed_bringup/maps/ and publishes it on /map.
A lifecycle manager auto-activates the map_server node.

Usage (standalone):
    ros2 launch testbed_navigation map_loader.launch.py
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # Locate the map YAML installed by testbed_bringup
    map_yaml = os.path.join(
        get_package_share_directory('testbed_bringup'),
        'maps',
        'testbed_world.yaml',
    )

    # Nav2 config from this package
    nav_config = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config',
        'map_server_params.yaml',
    )

    # --- Map Server ---
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            nav_config,
            {'yaml_filename': map_yaml},
        ],
    )

    # --- Lifecycle Manager (activates map_server) ---
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server'],
        }],
    )

    return LaunchDescription([
        map_server_node,
        lifecycle_manager,
    ])

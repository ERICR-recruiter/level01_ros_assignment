#!/usr/bin/env python3
"""
localization.launch.py — Map Server + AMCL for Testbed-T1.0.0

Starts map_server and amcl, managed by a single lifecycle manager.
AMCL provides the map → odom transform required by Nav2.

The initial pose matches the Gazebo spawn position (0.0, 5.0, yaw 0.0).

Usage (standalone — requires running Gazebo simulation):
    ros2 launch testbed_navigation localization.launch.py
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    pkg_share = get_package_share_directory('testbed_navigation')

    map_yaml = os.path.join(
        get_package_share_directory('testbed_bringup'),
        'maps',
        'testbed_world.yaml',
    )

    map_server_params = os.path.join(pkg_share, 'config', 'map_server_params.yaml')
    amcl_params = os.path.join(pkg_share, 'config', 'amcl_params.yaml')

    # --- Map Server ---
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            map_server_params,
            {'yaml_filename': map_yaml},
        ],
    )

    # --- AMCL ---
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params],
    )

    # --- Lifecycle Manager (activates map_server then amcl) ---
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }],
    )

    return LaunchDescription([
        map_server_node,
        amcl_node,
        lifecycle_manager,
    ])

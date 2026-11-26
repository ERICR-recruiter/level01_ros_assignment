#!/usr/bin/env python3
"""
navigation.launch.py — Nav2 planning, control and recovery for Testbed-T1.0.0

Starts the following Nav2 nodes (each one is a lifecycle node):
  • planner_server   — NavfnPlanner global planner
  • controller_server — DWB local planner
  • behavior_server   — Spin / BackUp / Wait recoveries
  • bt_navigator      — BehaviorTree-based NavigateToPose

A lifecycle manager auto-activates all four nodes.

Prerequisite: map_server and amcl must already be running and active
(e.g. via localization.launch.py).

Usage (standalone — after starting simulation + localization):
    ros2 launch testbed_navigation navigation.launch.py
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node


def generate_launch_description():

    pkg_share = get_package_share_directory('testbed_navigation')

    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')

    bt_xml = os.path.join(
        pkg_share, 'behavior_trees', 'navigate_to_pose.xml'
    )

    # --- Planner Server ---
    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params],
    )

    # --- Controller Server ---
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params],
    )

    # --- Behavior Server ---
    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_params],
    )

    # --- BT Navigator ---
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[
            nav2_params,
            {'default_bt_xml_filename': bt_xml},
        ],
    )

    # --- Lifecycle Manager ---
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'planner_server',
                'controller_server',
                'behavior_server',
                'bt_navigator',
            ],
        }],
    )

    return LaunchDescription([
        planner_server,
        controller_server,
        behavior_server,
        bt_navigator,
        lifecycle_manager,
    ])

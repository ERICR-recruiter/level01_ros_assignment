#!/usr/bin/env python3
"""Bring up localization and the nav2 navigation servers (planner, controller,
behavior, bt_navigator), then drive them through their lifecycle transitions."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Launch all components needed for the testbed robot to navigate."""
    navigation_share = get_package_share_directory('testbed_navigation')
    params_file = os.path.join(navigation_share, 'config', 'nav2_params.yaml')

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'localization.launch.py',
            )
        )
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[params_file],
    )

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[params_file],
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[params_file],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[params_file],
    )

    # Wait for localization (map_server + amcl) to finish activating first.
    configure_navigation = TimerAction(
        period=12.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/planner_server', 'configure'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/controller_server', 'configure'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/behavior_server', 'configure'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/bt_navigator', 'configure'],
                output='screen',
            ),
        ],
    )

    activate_navigation = TimerAction(
        period=14.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/planner_server', 'activate'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/controller_server', 'activate'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/behavior_server', 'activate'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/bt_navigator', 'activate'],
                output='screen',
            ),
        ],
    )

    return LaunchDescription([
        localization,
        planner_server,
        controller_server,
        behavior_server,
        bt_navigator,
        configure_navigation,
        activate_navigation,
    ])

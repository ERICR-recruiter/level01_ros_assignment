#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    """Start the map server and automatically move it to the active state."""
    package_share = get_package_share_directory('testbed_bringup')
    map_yaml = os.path.join(package_share, 'maps', 'testbed_world.yaml')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml,
            'use_sim_time': True,
        }],
    )

    configure_map_server = TimerAction(
        period=2.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'lifecycle', 'set', '/map_server', 'configure'],
            output='screen',
        )],
    )

    activate_map_server = TimerAction(
        period=4.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'lifecycle', 'set', '/map_server', 'activate'],
            output='screen',
        )],
    )

    return LaunchDescription([
        map_server,
        configure_map_server,
        activate_map_server,
    ])

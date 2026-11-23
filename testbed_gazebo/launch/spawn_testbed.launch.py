#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg_description = get_package_share_directory('testbed_description')

    robot_description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_description,
                'launch',
                'robot_description.launch.py'
            )
        )
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_testbed',
        output='screen',
        arguments=[
            '-name', 'testbed',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '5.0',
            '-z', '0.1'
        ]
    )

    delayed_spawn = TimerAction(
        period=3.0,
        actions=[spawn_robot]
    )

    return LaunchDescription([
        robot_description_launch,
        delayed_spawn
    ])

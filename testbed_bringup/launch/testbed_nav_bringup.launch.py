#!/usr/bin/python3
"""
testbed_nav_bringup.launch.py
-------------------------------
Combined launch: Gazebo simulation + full Nav2 navigation stack in ONE command.

Usage:
    ros2 launch testbed_bringup testbed_nav_bringup.launch.py

This avoids the need for two separate terminals / containers.
Starts:
  1. Gazebo + robot spawn (testbed_full_bringup.launch.py)
  2. Nav2 full stack (navigation.launch.py) after a 10-second delay
     so Gazebo has time to start publishing /scan and /odom.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    pkg_testbed_bringup    = get_package_share_directory('testbed_bringup')
    pkg_testbed_navigation = get_package_share_directory('testbed_navigation')

    default_map_yaml = os.path.join(pkg_testbed_bringup, 'maps', 'testbed_world.yaml')

    # --- Gazebo + Robot + RViz ---
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_bringup, 'launch', 'testbed_full_bringup.launch.py')
        )
    )

    # --- Nav2 stack — delayed 10 s to let Gazebo start publishing topics ---
    navigation = TimerAction(
        period=10.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_testbed_navigation, 'launch', 'navigation.launch.py')
                ),
                launch_arguments={
                    'map': LaunchConfiguration('map'),
                }.items()
            )
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=default_map_yaml,
            description='Full path to map YAML file'
        ),
        simulation,
        navigation,
    ])

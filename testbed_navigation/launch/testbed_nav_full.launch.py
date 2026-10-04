#!/usr/bin/env python3
"""Convenience launch: map_loader + localization + navigation (+ optional RViz).

The three stages stay independent launch files; this one only includes them, so the
modular files can still be started one by one in separate terminals.

    # terminal 1: simulation
    ros2 launch testbed_bringup testbed_full_bringup.launch.py
    # terminal 2: whole navigation chain
    ros2 launch testbed_navigation testbed_nav_full.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    launch_dir = os.path.join(get_package_share_directory('testbed_navigation'), 'launch')
    use_sim_time = LaunchConfiguration('use_sim_time')

    def include(name, **kwargs):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)),
            launch_arguments={'use_sim_time': use_sim_time}.items(),
            **kwargs)

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Also open the navigation RViz config'),
        include('map_loader.launch.py'),
        include('localization.launch.py'),
        include('navigation.launch.py'),
        include('rviz.launch.py', condition=IfCondition(LaunchConfiguration('rviz'))),
    ])

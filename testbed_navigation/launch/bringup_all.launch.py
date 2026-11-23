#!/usr/bin/env python3
"""Convenience wrapper: map_loader + localization + navigation (+ optional RViz).

The three component launch files stay independent (run them separately for
testing); this file only includes them. Start the simulation first:
  ros2 launch testbed_bringup testbed_full_bringup.launch.py
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

    def include(name, **kw):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)), **kw)

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Also open the navigation RViz layout'),
        include('map_loader.launch.py'),
        include('localization.launch.py'),
        include('navigation.launch.py'),
        include('rviz.launch.py', condition=IfCondition(LaunchConfiguration('rviz'))),
    ])

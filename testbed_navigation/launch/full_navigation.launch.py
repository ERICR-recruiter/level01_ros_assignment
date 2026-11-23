#!/usr/bin/env python3
"""Convenience wrapper: map_loader + localization + navigation (+ optional RViz).
Each piece can still be started on its own."""
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

    def include(name, **kw):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)), **kw)

    args = {'use_sim_time': use_sim_time}.items()
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        include('map_loader.launch.py', launch_arguments=args),
        include('localization.launch.py', launch_arguments=args),
        include('navigation.launch.py', launch_arguments=args),
        include('rviz.launch.py', launch_arguments=args, condition=IfCondition(LaunchConfiguration('rviz'))),
    ])

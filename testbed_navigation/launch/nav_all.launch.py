#!/usr/bin/env python3
"""Convenience: map_loader + localization + navigation (+ optional RViz)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')
    launch_dir = os.path.join(nav_pkg, 'launch')

    def include(name):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)))

    rviz = Node(
        package='rviz2', executable='rviz2', name='rviz_nav',
        arguments=['-d', os.path.join(nav_pkg, 'rviz', 'navigation.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen')

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Also start a Nav2 RViz'),
        include('map_loader.launch.py'),
        include('localization.launch.py'),
        include('navigation.launch.py'),
        rviz,
    ])

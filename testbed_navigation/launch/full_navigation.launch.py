#!/usr/bin/env python3
"""Convenience launch: map loader + localization + navigation + RViz (nav view).

This only *includes* the three individual launch files, so each component can
still be started and tested on its own. Start the simulation first:

  ros2 launch testbed_bringup testbed_full_bringup.launch.py   # Gazebo + its own RViz
  ros2 launch testbed_navigation full_navigation.launch.py     # this file

Set `rviz:=false` if you prefer to keep using the RViz window from the bringup.
"""
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

    use_sim_time = LaunchConfiguration('use_sim_time')

    def include(name):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)),
            launch_arguments={'use_sim_time': use_sim_time}.items())

    rviz = Node(
        package='rviz2', executable='rviz2', name='nav_rviz', output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(LaunchConfiguration('rviz')))

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Also start RViz with the navigation layout'),
        DeclareLaunchArgument(
            'rvizconfig',
            default_value=os.path.join(nav_pkg, 'rviz', 'navigation.rviz'),
            description='RViz config file'),
        include('map_loader.launch.py'),
        include('localization.launch.py'),
        include('navigation.launch.py'),
        rviz,
    ])

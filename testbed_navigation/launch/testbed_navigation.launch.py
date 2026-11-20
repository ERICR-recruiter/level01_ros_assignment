#!/usr/bin/env python3
"""Convenience launch: map + localization + navigation + RViz (Nav2 view).

Run the simulation first (ros2 launch testbed_bringup testbed_full_bringup.launch.py),
then:
    ros2 launch testbed_navigation testbed_navigation.launch.py
Each stage can also be started on its own with map_loader / localization / navigation.launch.py.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')
    bringup_share = get_package_share_directory('testbed_bringup')
    launch_dir = os.path.join(nav_share, 'launch')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')

    def include(name, args):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)),
            launch_arguments=args.items())

    return LaunchDescription([
        DeclareLaunchArgument(
            'map', default_value=os.path.join(bringup_share, 'maps', 'testbed_world.yaml')),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),

        include('localization.launch.py',      # includes map_loader.launch.py
                {'map': map_yaml, 'use_sim_time': use_sim_time}),
        # give AMCL a moment to publish map->odom before the costmaps start
        TimerAction(period=3.0, actions=[
            include('navigation.launch.py', {'use_sim_time': use_sim_time})]),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2_nav',
            condition=IfCondition(use_rviz),
            arguments=['-d', os.path.join(nav_share, 'rviz', 'testbed_navigation.rviz')],
            parameters=[{'use_sim_time': use_sim_time}],
            output='log'),
    ])

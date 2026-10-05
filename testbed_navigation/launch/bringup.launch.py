#!/usr/bin/env python3
# Convenience launch: localization + navigation + RViz in one go.
# Gazebo and the robot (testbed_bringup) are expected to be running separately.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')
    launch_dir = os.path.join(nav_pkg, 'launch')

    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz_config = LaunchConfiguration('rviz_config')

    default_rviz = os.path.join(nav_pkg, 'rviz', 'navigation.rviz')

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'localization.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'navigation.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}])

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo /clock instead of wall time'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz,
                              description='RViz config to open with the navigation view'),
        localization,
        navigation,
        rviz,
    ])
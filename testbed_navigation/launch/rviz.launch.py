#!/usr/bin/env python3
"""Optional - RViz with the displays needed to check map / localization / navigation.

The base bring-up already opens RViz (testbed_description/rviz/full_bringup.rviz) but that
config has no Map, costmap, particle-cloud or path displays. Use this one for the checks.

    ros2 launch testbed_navigation rviz.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('testbed_navigation')

    return LaunchDescription([
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(pkg, 'rviz', 'testbed_nav.rviz'),
            description='Absolute path to the RViz config'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2_nav',
            output='screen',
            arguments=['-d', LaunchConfiguration('rviz_config')],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        ),
    ])

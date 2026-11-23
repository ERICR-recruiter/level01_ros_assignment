#!/usr/bin/env python3
"""Optional: RViz with the navigation layout (map, particles, costmaps, plans).

testbed_full_bringup already opens an RViz window (fixed frame = odom). Either
use this launch file in addition, or just close the first window.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('testbed_navigation')
    return LaunchDescription([
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(pkg_nav, 'rviz', 'navigation.rviz')),
        Node(
            package='rviz2', executable='rviz2', name='rviz_nav',
            arguments=['-d', LaunchConfiguration('rviz_config')],
            parameters=[{'use_sim_time': True}],
            output='screen'),
    ])

#!/usr/bin/env python3
"""RViz with a navigation layout (fixed frame = map, 2D Pose Estimate, Nav2 Goal)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'rviz_config', default_value=os.path.join(nav_dir, 'rviz', 'navigation.rviz')),
        Node(package='rviz2', executable='rviz2', name='rviz2_nav', output='screen',
             arguments=['-d', LaunchConfiguration('rviz_config')],
             parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]),
    ])

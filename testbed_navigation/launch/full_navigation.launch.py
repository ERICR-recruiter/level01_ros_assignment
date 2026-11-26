#!/usr/bin/env python3
"""
full_navigation.launch.py — Complete Nav2 stack for Testbed-T1.0.0

Composes localization (map_server + amcl) and navigation (planner,
controller, behavior, bt_navigator) into a single launch command.

Also starts RViz2 with the navigation-specific configuration.

Prerequisite: Gazebo simulation must already be running:
    ros2 launch testbed_bringup testbed_full_bringup.launch.py

Usage:
    ros2 launch testbed_navigation full_navigation.launch.py
    ros2 launch testbed_navigation full_navigation.launch.py use_rviz:=false
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_share = get_package_share_directory('testbed_navigation')

    # --- Launch arguments ---
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Start RViz2 with navigation config',
    )

    # --- Include localization (map_server + amcl) ---
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'localization.launch.py'),
        ),
    )

    # --- Include navigation (planner + controller + behavior + bt) ---
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'navigation.launch.py'),
        ),
    )

    # --- RViz2 ---
    rviz_config = os.path.join(pkg_share, 'rviz', 'navigation.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_nav',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    )

    return LaunchDescription([
        use_rviz_arg,
        localization,
        navigation,
        rviz_node,
    ])

#!/usr/bin/env python3
"""Localization launch file for Testbed robot.

Manually launches nav2_amcl and transitions its lifecycle state using
nav2_lifecycle_manager, without relying on nav2_bringup.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(nav_pkg, 'config', 'amcl_params.yaml'),
        description='Full path to parameter file for AMCL')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 lifecycle stack')

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            params_file,
            {'use_sim_time': use_sim_time},
        ],
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': ['amcl'],
        }],
    )

    return LaunchDescription([
        declare_params,
        declare_use_sim_time,
        declare_autostart,
        amcl_node,
        lifecycle_manager_node,
    ])

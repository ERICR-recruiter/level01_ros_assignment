#!/usr/bin/env python3
"""Run the Nav2 navigation servers one by one (no nav2_bringup).

Nodes: controller_server (DWB), planner_server (NavFn), behavior_server,
bt_navigator, plus a lifecycle manager. Needs map + AMCL running.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('nav2_params_file')

    common = dict(output='screen',
                  parameters=[params_file, {'use_sim_time': use_sim_time}])

    controller_server = Node(
        package='nav2_controller', executable='controller_server',
        name='controller_server', **common)

    planner_server = Node(
        package='nav2_planner', executable='planner_server',
        name='planner_server', **common)

    behavior_server = Node(
        package='nav2_behaviors', executable='behavior_server',
        name='behavior_server', **common)

    bt_navigator = Node(
        package='nav2_bt_navigator', executable='bt_navigator',
        name='bt_navigator', **common)

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['controller_server',
                                    'planner_server',
                                    'behavior_server',
                                    'bt_navigator']}],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock'),
        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=os.path.join(nav_pkg, 'config', 'nav2_params.yaml'),
            description='Nav2 parameter file'),
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        lifecycle_manager,
    ])

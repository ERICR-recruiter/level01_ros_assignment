#!/usr/bin/env python3
"""Bring up the Nav2 servers one by one: controller, planner, behaviours, BT navigator,
velocity smoother. No nav2_bringup involved.

cmd_vel chain:  controller_server -> /cmd_vel_nav -> velocity_smoother -> /cmd_vel -> diff drive
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params = LaunchConfiguration('params_file')
    common = [params, {'use_sim_time': use_sim_time}]

    controller_server = Node(
        package='nav2_controller', executable='controller_server',
        name='controller_server', output='screen', parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav')])

    planner_server = Node(
        package='nav2_planner', executable='planner_server',
        name='planner_server', output='screen', parameters=common)

    behavior_server = Node(
        package='nav2_behaviors', executable='behavior_server',
        name='behavior_server', output='screen', parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav')])

    bt_navigator = Node(
        package='nav2_bt_navigator', executable='bt_navigator',
        name='bt_navigator', output='screen', parameters=common)

    velocity_smoother = Node(
        package='nav2_velocity_smoother', executable='velocity_smoother',
        name='velocity_smoother', output='screen', parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav'), ('cmd_vel_smoothed', 'cmd_vel')])

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_navigation', output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['controller_server', 'planner_server', 'behavior_server',
                           'bt_navigator', 'velocity_smoother'],
        }])

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'nav2_params.yaml')),
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        velocity_smoother,
        lifecycle_manager,
    ])

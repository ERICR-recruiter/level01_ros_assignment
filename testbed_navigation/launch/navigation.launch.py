#!/usr/bin/env python3
"""Bring up the Nav2 planner/controller/BT stack node by node (no nav2_bringup)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

LIFECYCLE_NODES = [
    'controller_server',
    'smoother_server',
    'planner_server',
    'behavior_server',
    'bt_navigator',
    'waypoint_follower',
    'velocity_smoother',
]

# Let node namespaces be prepended to /tf and /tf_static.
TF_REMAPPINGS = [('/tf', 'tf'), ('/tf_static', 'tf_static')]


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    bt_dir = get_package_share_directory('nav2_bt_navigator')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    bt_xml = os.path.join(
        bt_dir, 'behavior_trees', 'navigate_to_pose_w_replanning_and_recovery.xml')

    params = [params_file, {'use_sim_time': use_sim_time}]

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'nav2_params.yaml'),
            description='Full path to the Nav2 parameter file'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo simulation clock'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically activate the navigation nodes'),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=params,
            remappings=TF_REMAPPINGS + [('cmd_vel', 'cmd_vel_nav')]),
        Node(
            package='nav2_smoother',
            executable='smoother_server',
            name='smoother_server',
            output='screen',
            parameters=params,
            remappings=TF_REMAPPINGS),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=params,
            remappings=TF_REMAPPINGS),
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=params,
            remappings=TF_REMAPPINGS),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=params + [{
                'default_nav_to_pose_bt_xml': bt_xml,
                'default_nav_through_poses_bt_xml': os.path.join(
                    bt_dir, 'behavior_trees',
                    'navigate_through_poses_w_replanning_and_recovery.xml'),
            }],
            remappings=TF_REMAPPINGS),
        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=params,
            remappings=TF_REMAPPINGS),
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=params,
            remappings=TF_REMAPPINGS + [
                ('cmd_vel', 'cmd_vel_nav'),
                ('cmd_vel_smoothed', 'cmd_vel'),
            ]),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': autostart,
                'node_names': LIFECYCLE_NODES,
            }]),
    ])

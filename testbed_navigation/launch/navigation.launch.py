#!/usr/bin/env python3
"""Launch the Nav2 planner, controller, behavior tree, and velocity smoother.

The map server and AMCL must be running first. The planner and controller each
host their own costmap.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('testbed_navigation')
    nav2_params = os.path.join(pkg, 'config', 'nav2_params.yaml')
    bt_dir = os.path.join(pkg, 'behavior_trees')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Resolve the trees from the installed package share directory.
    bt_params = {
        'default_nav_to_pose_bt_xml': os.path.join(bt_dir, 'navigate_to_pose.xml'),
        'default_nav_through_poses_bt_xml': os.path.join(bt_dir, 'navigate_through_poses.xml'),
    }

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the /clock topic from Gazebo rather than wall time.',
        ),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
        ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
            remappings=[('cmd_vel', 'cmd_vel_nav')],
        ),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_params, bt_params, {'use_sim_time': use_sim_time}],
        ),

        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
            remappings=[
                ('cmd_vel', 'cmd_vel_nav'),
                ('cmd_vel_smoothed', 'cmd_vel'),
            ],
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': [
                    'planner_server',
                    'behavior_server',
                    'controller_server',
                    'bt_navigator',
                    'velocity_smoother',
                ],
                'start_order': [
                    'planner_server',
                    'behavior_server',
                    'controller_server',
                    'bt_navigator',
                    'velocity_smoother',
                ],
            }],
        ),
    ])

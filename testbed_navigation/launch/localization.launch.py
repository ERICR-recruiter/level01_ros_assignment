#!/usr/bin/env python3
"""Launch AMCL after Gazebo and the map are available.

The initial pose defaults to the robot's spawn point. Use initial_x, initial_y,
and initial_yaw to provide a different estimate.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('testbed_navigation')
    amcl_params = os.path.join(pkg, 'config', 'amcl_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the /clock topic from Gazebo rather than wall time.',
        ),
        DeclareLaunchArgument(
            'initial_x',
            default_value='0.0',
            description='Initial guess for the robot x position, metres.',
        ),
        DeclareLaunchArgument(
            'initial_y',
            default_value='5.0',
            description='Initial guess for the robot y position, metres.',
        ),
        DeclareLaunchArgument(
            'initial_yaw',
            default_value='0.0',
            description='Initial guess for the robot yaw, radians.',
        ),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[
                amcl_params,
                {
                    'use_sim_time': LaunchConfiguration('use_sim_time'),
                    'set_initial_pose': True,
                    'initial_pose.x': LaunchConfiguration('initial_x'),
                    'initial_pose.y': LaunchConfiguration('initial_y'),
                    'initial_pose.yaw': LaunchConfiguration('initial_yaw'),
                },
            ],
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'autostart': True,
                'node_names': ['amcl'],
            }],
        ),
    ])
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    entity_name = LaunchConfiguration('entity_name')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')
    yaw = LaunchConfiguration('yaw')

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', entity_name,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-R', '0.0',
            '-P', '0.0',
            '-Y', yaw,
            '-topic', '/robot_description',
            '-timeout', '60',
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'entity_name',
            default_value='testbed',
            description='Name of the spawned robot entity in Gazebo',
        ),
        DeclareLaunchArgument(
            'x_pose',
            default_value='0.0',
            description='Initial X spawn coordinate (meters)',
        ),
        DeclareLaunchArgument(
            'y_pose',
            default_value='5.0',
            description='Initial Y spawn coordinate (meters)',
        ),
        DeclareLaunchArgument(
            'z_pose',
            default_value='0.01',
            description='Initial Z spawn coordinate (meters) with ground clearance',
        ),
        DeclareLaunchArgument(
            'yaw',
            default_value='0.0',
            description='Initial yaw orientation (radians)',
        ),
        spawn_robot,
    ])

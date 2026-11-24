#!/usr/bin/python3
# -*- coding: utf-8 -*-
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.05')
    yaw_pose = LaunchConfiguration('yaw_pose', default='0.0')
    robot_base_name = LaunchConfiguration('robot_name', default='testbed')

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', robot_base_name,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-Y', yaw_pose,
            '-topic', '/robot_description'
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument('x_pose', default_value='0.0', description='Initial X position'),
        DeclareLaunchArgument('y_pose', default_value='0.0', description='Initial Y position'),
        DeclareLaunchArgument('z_pose', default_value='0.05', description='Initial Z position'),
        DeclareLaunchArgument('yaw_pose', default_value='0.0', description='Initial Yaw orientation'),
        DeclareLaunchArgument('robot_name', default_value='testbed', description='Robot entity name'),
        spawn_robot,
    ])

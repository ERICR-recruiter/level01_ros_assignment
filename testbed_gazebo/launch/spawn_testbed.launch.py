#!/usr/bin/python3
# -*- coding: utf-8 -*-
from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node


def generate_launch_description():
    position = [0.0, 5.0, 0.02]
    orientation = [0.0, 0.0, 0.0]
    entity_name = 'testbed'

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-name', entity_name,
            '-topic', '/robot_description',
            '-x', str(position[0]),
            '-y', str(position[1]),
            '-z', str(position[2]),
            '-R', str(orientation[0]),
            '-P', str(orientation[1]),
            '-Y', str(orientation[2]),
        ],
    )

    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_base_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    load_controllers_after_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[
                joint_state_broadcaster_spawner,
                diff_drive_controller_spawner,
            ],
        )
    )

    return LaunchDescription([
        gz_bridge,
        spawn_robot,
        load_controllers_after_spawn,
    ])

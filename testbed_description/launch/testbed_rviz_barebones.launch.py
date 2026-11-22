#!/usr/bin/env python3

from launch import LaunchDescription
from launch.substitutions import (
    Command,
    FindExecutable,
    PathJoinSubstitution
)

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Locate robot description package
    description_package = FindPackageShare(
        'testbed_description'
    )

    # Generate robot description from Xacro
    robot_description_content = Command([
        FindExecutable(name='xacro'),
        ' ',
        PathJoinSubstitution([
            description_package,
            'urdf',
            'testbed.xacro'
        ])
    ])

    robot_description = {
        'robot_description': robot_description_content
    }

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': False}
        ]
    )

    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    # RViz configuration
    rviz_config = PathJoinSubstitution([
        description_package,
        'rviz',
        'testbed_barebones.rviz'
    ])

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[
            {'use_sim_time': False}
        ]
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz_node
    ])


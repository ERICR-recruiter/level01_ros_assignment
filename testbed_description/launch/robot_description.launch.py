#!/usr/bin/env python3

from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([
            FindPackageShare("testbed_description"),
            "urdf",
            "testbed.xacro",
            ]),
    ])

    robot_description = {"robot_description": robot_description_content}
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
<<<<<<< HEAD
            parameters=[robot_description, {'use_sim_time': True}]),
    ])

# using sim time for tf timing errors in Nav2
=======
            parameters=[robot_description]),
    ])
>>>>>>> 6086b810674fdc480a963e55ace0626ed9b7837b

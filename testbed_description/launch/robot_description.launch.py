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
            # BUG FIX: Added use_sim_time=True so robot_state_publisher uses
            # Gazebo simulation clock instead of wall clock. Without this,
            # TF transforms are published with wall-time stamps while all
            # sensor data uses sim time, causing TF lookup failures and
            # breaking AMCL/Nav2 entirely.
            parameters=[robot_description, {'use_sim_time': True}]),
    ])
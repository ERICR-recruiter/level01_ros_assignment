#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    position = (0.0, 5.0, 0.0)
    orientation = (0.0, 0.0, 0.0)
    entity_name = "testbed"

    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="spawn_entity",
        output="screen",
        arguments=[
            "-entity", entity_name,
            "-x", str(position[0]),
            "-y", str(position[1]),
            "-z", str(position[2]),
            "-R", str(orientation[0]),
            "-P", str(orientation[1]),
            "-Y", str(orientation[2]),
            "-topic", "/robot_description",
        ],
    )

    return LaunchDescription([spawn_robot])

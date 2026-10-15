#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random

from launch_ros.actions import Node
from launch import LaunchDescription


# Entry point used by the launch system.
def generate_launch_description():


    # Robot position and orientation in the world.
    # Position: [x, y, z]
    position = [0.0, 5.0, 0.0]
    # Orientation: [roll, pitch, yaw]
    orientation = [0.0, 0.0, 0.0]
    # Robot base name.
    robot_base_name = "testbed"


    entity_name = robot_base_name#+"-"+str(int(random.random()*100000))

    # Spawn the robot in Gazebo.
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=['-entity',
                   entity_name,
                   '-x', str(position[0]), '-y', str(position[1]
                                                     ), '-z', str(position[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]
                                                        ), '-Y', str(orientation[2]),
                   '-topic', '/robot_description'
                   ]
    )

 

    # Return the launch description.
    return LaunchDescription(
        [
            spawn_robot,
        ]
    )

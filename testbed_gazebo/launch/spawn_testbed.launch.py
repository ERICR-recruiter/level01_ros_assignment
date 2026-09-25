#!/usr/bin/python3
# -*- coding: utf-8 -*-
from launch_ros.actions import Node
from launch import LaunchDescription


# this is the function launch  system will look for
def generate_launch_description():

    # Position and orientation
    # [X, Y, Z]
    position = [0.0, 5.0, 0.0]
    # [Roll, Pitch, Yaw]
    orientation = [0.0, 0.0, 0.0]
    # Base Name or robot
    robot_base_name = "testbed"

    entity_name = robot_base_name

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_entity',
        output='screen',
        arguments=['-name',
                   entity_name,
                   '-x', str(position[0]), '-y', str(position[1]
                                                     ), '-z', str(position[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]
                                                        ), '-Y', str(orientation[2]),
                   '-topic', '/robot_description'
                   ]
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='testbed_bridge',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        ],
    )

    # create and return launch description object
    return LaunchDescription(
        [
            spawn_robot,
            bridge,
        ]
    )

#!/usr/bin/python3
# -*- coding: utf-8 -*-
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # Position and orientation
    # [X, Y, Z]
    position = [0.0, 5.0, 0.0]
    # [Roll, Pitch, Yaw]
    orientation = [0.0, 0.0, 0.0]
    # Base Name of robot
    robot_base_name = "testbed"

    entity_name = robot_base_name

    # Spawn entity node for Ignition / Gazebo Sim
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-name', entity_name,
            '-x', str(position[0]),
            '-y', str(position[1]),
            '-z', str(position[2]),
            '-R', str(orientation[0]),
            '-P', str(orientation[1]),
            '-Y', str(orientation[2]),
            '-topic', 'robot_description'
        ]
    )

    # Bridge between Ignition/Gazebo and ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Joint States (Gz -> ROS 2)
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            # Odometry topics emitted by Gazebo can be either directly under /odom or under the model namespace.
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/model/testbed/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            # TF transforms (Gz -> ROS 2)
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/model/testbed/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            # Velocity commands (ROS 2 -> Gz)
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            # Lidar Scan (Gz -> ROS 2)
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            # IMU (Gz -> ROS 2)
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU'
        ],
        remappings=[
            ('/model/testbed/tf', '/tf'),
            ('/model/testbed/odometry', '/odom'),
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        spawn_robot,
        bridge
    ])
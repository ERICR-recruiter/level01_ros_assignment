#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')

    world = LaunchConfiguration('world')
    headless = LaunchConfiguration('headless')
    gz_launch = os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')

    gazebo_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch),
        launch_arguments={
            'gz_args': ['-r -v 2 ', world],
            'on_exit_shutdown': 'true',
        }.items(),
        condition=UnlessCondition(headless),
    )

    gazebo_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch),
        launch_arguments={
            'gz_args': ['-r -s --headless-rendering -v 2 ', world],
            'on_exit_shutdown': 'true',
        }.items(),
        condition=IfCondition(headless),
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[{
            'config_file': os.path.join(pkg_testbed_gazebo, 'config', 'bridge.yaml'),
            'use_sim_time': True,
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_testbed_gazebo, 'worlds', 'testbed_playground.world'),
            description='SDF world file'),
        DeclareLaunchArgument(
            'headless',
            default_value='false',
            description='Run the Gazebo server without a GUI'),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', os.path.join(pkg_testbed_gazebo, 'models')),
        gazebo_gui,
        gazebo_headless,
        bridge,
    ])

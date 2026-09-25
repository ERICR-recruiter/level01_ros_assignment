#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')

    description_package_name = "testbed_description"
    install_dir = get_package_prefix(description_package_name)

    gazebo_models_path = os.path.join(pkg_testbed_gazebo, 'models')

    resource_path = os.pathsep.join([
        os.path.join(install_dir, 'share'),
        gazebo_models_path,
    ])
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        resource_path = os.environ['GZ_SIM_RESOURCE_PATH'] + os.pathsep + resource_path

    world = LaunchConfiguration('world')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'),
        ),
        launch_arguments={'gz_args': ['-r -v 4 ', world]}.items(),
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        output='screen',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
    )

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),
        DeclareLaunchArgument(
          'world',
          default_value=os.path.join(pkg_testbed_gazebo, 'worlds', 'testbed_playground.world'),
          description='SDF world file'),
        gz_sim,
        clock_bridge,
    ])

#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')

    description_package_name = 'testbed_description'
    install_dir = get_package_prefix(description_package_name)
    gazebo_models_path = os.path.join(pkg_testbed_gazebo, 'models')

    resource_paths = [
        os.path.join(install_dir, 'share'),
        gazebo_models_path,
    ]
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        resource_paths.append(os.environ['GZ_SIM_RESOURCE_PATH'])

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=':'.join(resource_paths),
    )

    world_file = os.path.join(pkg_testbed_gazebo, 'worlds', 'testbed_playground.world')

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=world_file,
        description='SDF world file',
    )

    declare_headless = DeclareLaunchArgument(
        'headless',
        default_value='false',
        description='Run Gazebo Sim server only (headless) if true',
    )

    gz_sim_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        condition=UnlessCondition(LaunchConfiguration('headless')),
        launch_arguments={
            'gz_args': ['-r ', LaunchConfiguration('world')],
        }.items(),
    )

    gz_sim_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('headless')),
        launch_arguments={
            'gz_args': ['-s -r ', LaunchConfiguration('world')],
        }.items(),
    )

    return LaunchDescription([
        declare_world,
        declare_headless,
        set_gz_resource_path,
        gz_sim_gui,
        gz_sim_headless,
    ])

#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')

    description_package_name = "testbed_description"
    install_dir = get_package_prefix(description_package_name)

    gazebo_models_path = os.path.join(pkg_testbed_gazebo, 'models')

    # Ignition Gazebo (Fortress) uses IGN_GAZEBO_RESOURCE_PATH instead of GAZEBO_MODEL_PATH
    if 'IGN_GAZEBO_RESOURCE_PATH' in os.environ:
        os.environ['IGN_GAZEBO_RESOURCE_PATH'] += f":{install_dir}/share:{gazebo_models_path}"
    else:
        os.environ['IGN_GAZEBO_RESOURCE_PATH'] = f"{install_dir}/share:{gazebo_models_path}"

    # Ignition Gazebo (Fortress) uses IGN_GAZEBO_SYSTEM_PLUGIN_PATH instead of GAZEBO_PLUGIN_PATH
    if 'IGN_GAZEBO_SYSTEM_PLUGIN_PATH' in os.environ:
        os.environ['IGN_GAZEBO_SYSTEM_PLUGIN_PATH'] += f":{install_dir}/lib"
    else:
        os.environ['IGN_GAZEBO_SYSTEM_PLUGIN_PATH'] = f"{install_dir}/lib"

    print("IGN GAZEBO RESOURCE PATH==" + str(os.environ["IGN_GAZEBO_RESOURCE_PATH"]))
    print("IGN GAZEBO SYSTEM PLUGIN PATH==" + str(os.environ["IGN_GAZEBO_SYSTEM_PLUGIN_PATH"]))

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_testbed_gazebo, 'worlds', 'testbed_playground.world'),
        description='SDF world file'
    )

    # Ignition Gazebo launch using ros_gz_sim
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r ', LaunchConfiguration('world')]
        }.items()
    )

    return LaunchDescription([
        world_arg,
        gz_sim,
    ])
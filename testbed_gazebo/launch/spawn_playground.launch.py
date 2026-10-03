#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    pkg_gazebo_ros = get_package_share_directory('ros_gz_sim')
    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')

    description_package_name = "testbed_description"
    install_dir = get_package_prefix(description_package_name)

    gazebo_models_path = os.path.join(pkg_testbed_gazebo, 'models')

    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        os.environ['GZ_SIM_RESOURCE_PATH'] += ':' + install_dir + '/share:' + gazebo_models_path
    else:
        os.environ['GZ_SIM_RESOURCE_PATH'] = install_dir + "/share:" + gazebo_models_path

    if 'GZ_SIM_SYSTEM_PLUGIN_PATH' in os.environ:
        os.environ['GZ_SIM_SYSTEM_PLUGIN_PATH'] += ':' + install_dir + '/lib'
    else:
        os.environ['GZ_SIM_SYSTEM_PLUGIN_PATH'] = install_dir + '/lib'

    default_world_path = os.path.join(pkg_testbed_gazebo, 'worlds', 'testbed_playground.world')

    print("GAZEBO MODELS PATH=="+str(os.environ["GZ_SIM_RESOURCE_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GZ_SIM_SYSTEM_PLUGIN_PATH"]))

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gz_sim.launch.py'), 
        ),
        launch_arguments={
            'gz_args': [LaunchConfiguration('world'), ' -r']
        }.items(),
    )    

    return LaunchDescription([
        DeclareLaunchArgument(
          'world',
          default_value=default_world_path,
          description='SDF world file'),
        gazebo,
    ])
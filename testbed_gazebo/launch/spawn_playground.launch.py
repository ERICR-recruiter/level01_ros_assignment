#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')

    description_package_name = 'testbed_description'
    install_dir = get_package_prefix(description_package_name)
    gazebo_ros_prefix = get_package_prefix('gazebo_ros')
    gazebo_models_path = os.path.join(pkg_testbed_gazebo, 'models')

    extra_model_paths = os.path.join(install_dir, 'share') + ':' + gazebo_models_path
    if 'GAZEBO_MODEL_PATH' in os.environ and os.environ['GAZEBO_MODEL_PATH']:
        os.environ['GAZEBO_MODEL_PATH'] = os.environ['GAZEBO_MODEL_PATH'] + ':' + extra_model_paths
    else:
        os.environ['GAZEBO_MODEL_PATH'] = extra_model_paths

    # Gazebo Classic resolves ROS 2 system plugins (init, factory, diff-drive,
    # sensors, etc.) from the ROS installation's lib directory. Do not rely
    # only on LD_LIBRARY_PATH: Gazebo uses GAZEBO_PLUGIN_PATH for plugin lookup.
    ros_gazebo_plugin_path = os.path.join(gazebo_ros_prefix, 'lib')
    extra_plugin_path = os.path.join(install_dir, 'lib')
    plugin_paths = [
        path for path in os.environ.get('GAZEBO_PLUGIN_PATH', '').split(os.pathsep)
        if path
    ]
    for plugin_path in (ros_gazebo_plugin_path, extra_plugin_path):
        if plugin_path not in plugin_paths:
            plugin_paths.append(plugin_path)
    os.environ['GAZEBO_PLUGIN_PATH'] = os.pathsep.join(plugin_paths)

    default_world = os.path.join(pkg_testbed_gazebo, 'worlds', 'testbed_playground.world')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'verbose': LaunchConfiguration('verbose'),
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Absolute path to the SDF world file',
        ),
        DeclareLaunchArgument(
            'verbose',
            default_value='false',
            description='Enable verbose Gazebo output',
        ),
        gazebo,
    ])

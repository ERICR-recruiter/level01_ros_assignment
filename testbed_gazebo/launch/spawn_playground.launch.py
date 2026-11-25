#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    gazebo_ros_share = get_package_share_directory('gazebo_ros')
    gazebo_share = get_package_share_directory('testbed_gazebo')
    description_prefix = get_package_prefix('testbed_description')

    models_path = os.path.join(gazebo_share, 'models')
    os.environ['GAZEBO_MODEL_PATH'] = os.pathsep.join(filter(None, [
        os.environ.get('GAZEBO_MODEL_PATH', ''),
        os.path.join(description_prefix, 'share'),
        models_path
    ]))
    os.environ['GAZEBO_PLUGIN_PATH'] = os.pathsep.join(filter(None, [
        os.environ.get('GAZEBO_PLUGIN_PATH', ''),
        os.path.join(description_prefix, 'lib')
    ]))

    world = LaunchConfiguration('world')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(gazebo_share, 'worlds', 'testbed_playground.world'),
            description='Absolute path to the Gazebo world file'
        ),
        gazebo
    ])

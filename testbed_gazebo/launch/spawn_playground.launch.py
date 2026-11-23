#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')
    pkg_testbed_description = get_package_share_directory('testbed_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    default_world = os.path.join(
        pkg_testbed_gazebo,
        'worlds',
        'testbed_playground.world'
    )

    models_path = os.path.join(pkg_testbed_gazebo, 'models')
    description_share = os.path.dirname(pkg_testbed_description)

    existing_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')

    resource_paths = [
        models_path,
        description_share,
        existing_resource_path
    ]

    gz_resource_path = ':'.join(path for path in resource_paths if path)

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': [
                '-r -v 4 ',
                LaunchConfiguration('world')
            ]
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='SDF world file'
        ),
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=gz_resource_path
        ),
        gazebo
    ])

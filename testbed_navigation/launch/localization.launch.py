#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    navigation_share = get_package_share_directory('testbed_navigation')

    amcl_params = os.path.join(
        navigation_share,
        'config',
        'amcl_params.yaml'
    )

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'map_loader.launch.py'
            )
        )
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_params,
            {'use_sim_time': True}
        ]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['amcl']
            }
        ]
    )

    return LaunchDescription([
        map_loader,
        amcl,
        lifecycle_manager
    ])

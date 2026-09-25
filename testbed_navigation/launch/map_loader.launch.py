#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_share = get_package_share_directory('testbed_navigation')
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')
    default_params = os.path.join(pkg_share, 'config', 'map_server_params.yaml')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('map_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites={
            'yaml_filename': map_yaml,
            'use_sim_time': use_sim_time,
        },
        convert_types=True)

    return LaunchDescription([
        DeclareLaunchArgument(
            'map', default_value=default_map,
            description='Full path to the map yaml file to serve'),
        DeclareLaunchArgument(
            'map_params_file', default_value=default_params,
            description='Parameter file for map_server'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the /clock published by Gazebo'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Let the lifecycle manager configure and activate map_server'),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[configured_params],
            remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'autostart': autostart,
                         'node_names': ['map_server']}]),
    ])

#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_share = get_package_share_directory('testbed_navigation')
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')
    default_params = os.path.join(pkg_share, 'config', 'amcl_params.yaml')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('amcl_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    with_map = LaunchConfiguration('with_map')

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites={'use_sim_time': use_sim_time},
        convert_types=True)

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'map_loader.launch.py')),
        condition=IfCondition(with_map),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
        }.items())

    return LaunchDescription([
        DeclareLaunchArgument(
            'map', default_value=default_map,
            description='Map to localize against, forwarded to map_loader'),
        DeclareLaunchArgument(
            'amcl_params_file', default_value=default_params,
            description='Parameter file for AMCL'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the /clock published by Gazebo'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Let the lifecycle manager configure and activate AMCL'),
        DeclareLaunchArgument(
            'with_map', default_value='true',
            description='Also start map_server; set false if a map is already being served'),

        map_loader,

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[configured_params],
            remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'autostart': autostart,
                         'node_names': ['amcl']}]),
    ])

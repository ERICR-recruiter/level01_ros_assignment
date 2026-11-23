#!/usr/bin/env python3
"""Step 2 - Localization.

Starts nav2_amcl/amcl and a lifecycle manager for it. AMCL subscribes to /map
(from map_loader.launch.py) and /scan, and publishes the map -> odom TF,
/amcl_pose and /particle_cloud.

By default this file also includes map_loader.launch.py so that localization
can be brought up on its own; pass `load_map:=false` if the map server is
already running.

    ros2 launch testbed_navigation localization.launch.py
"""
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
    nav_dir = get_package_share_directory('testbed_navigation')
    bringup_dir = get_package_share_directory('testbed_bringup')

    params_file = LaunchConfiguration('amcl_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')
    load_map = LaunchConfiguration('load_map')
    map_yaml = LaunchConfiguration('map')

    configured_params = RewrittenYaml(
        source_file=params_file,
        param_rewrites={'use_sim_time': use_sim_time},
        convert_types=True)

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav_dir, 'launch', 'map_loader.launch.py')),
        condition=IfCondition(load_map),
        launch_arguments={'map': map_yaml,
                          'use_sim_time': use_sim_time,
                          'autostart': autostart,
                          'log_level': log_level}.items())

    return LaunchDescription([
        DeclareLaunchArgument(
            'amcl_params_file',
            default_value=os.path.join(nav_dir, 'config', 'amcl_params.yaml'),
            description='AMCL parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('log_level', default_value='info'),
        DeclareLaunchArgument('load_map', default_value='true',
                              description='Also start the map server (map_loader.launch.py)'),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_dir, 'maps', 'testbed_world.yaml'),
            description='Map yaml used when load_map is true'),

        map_loader,

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[configured_params],
            arguments=['--ros-args', '--log-level', log_level]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time},
                        {'autostart': autostart},
                        {'node_names': ['amcl']}],
            arguments=['--ros-args', '--log-level', log_level]),
    ])

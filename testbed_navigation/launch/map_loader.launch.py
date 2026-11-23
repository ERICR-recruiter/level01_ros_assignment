#!/usr/bin/env python3
"""Step 1 - Map loading.

Starts nav2_map_server/map_server with the testbed map and a lifecycle manager
that configures + activates it. The occupancy grid is published (transient
local) on /map in the `map` frame.

    ros2 launch testbed_navigation map_loader.launch.py
    ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/other_map.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    bringup_dir = get_package_share_directory('testbed_bringup')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('map_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    # Inject the map path / sim time into the parameter file at launch time.
    configured_params = RewrittenYaml(
        source_file=params_file,
        param_rewrites={'yaml_filename': map_yaml, 'use_sim_time': use_sim_time},
        convert_types=True)

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_dir, 'maps', 'testbed_world.yaml'),
            description='Full path to the map yaml file to load'),
        DeclareLaunchArgument(
            'map_params_file',
            default_value=os.path.join(nav_dir, 'config', 'map_server_params.yaml'),
            description='map_server parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use Gazebo /clock'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Automatically configure+activate the map_server'),
        DeclareLaunchArgument('log_level', default_value='info'),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[configured_params],
            arguments=['--ros-args', '--log-level', log_level]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time},
                        {'autostart': autostart},
                        {'node_names': ['map_server']}],
            arguments=['--ros-args', '--log-level', log_level]),
    ])

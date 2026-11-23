#!/usr/bin/env python3
"""Load the testbed map with nav2_map_server (no nav2_bringup involved).

Starts two nodes:
  * map_server                 - lifecycle node that serves the occupancy grid on /map
  * lifecycle_manager_map      - configures + activates map_server (autostart)

Usage:
  ros2 launch testbed_navigation map_loader.launch.py
  ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/to/other_map.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')
    bringup_pkg = get_package_share_directory('testbed_bringup')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_args = [
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_pkg, 'maps', 'testbed_world.yaml'),
            description='Absolute path to the map yaml file'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_pkg, 'config', 'map_server_params.yaml'),
            description='Parameter file for map_server'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically configure and activate map_server'),
    ]

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {'yaml_filename': ParameterValue(map_yaml, value_type=str),
             'use_sim_time': use_sim_time},
        ],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': ['map_server'],
        }],
    )

    return LaunchDescription(declare_args + [map_server, lifecycle_manager])

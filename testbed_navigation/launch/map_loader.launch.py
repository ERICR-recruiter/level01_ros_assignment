#!/usr/bin/env python3
# Step 4 of the assignment: load the map by hand using the map_server plugin.
# map_server is a lifecycle node, so on its own it just sits there inactive -
# the lifecycle_manager is what actually configures and activates it.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # The map ships inside testbed_bringup, so grab it from there by default.
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'),
        'maps', 'testbed_world.yaml')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'yaml_filename': map_yaml}])

    # autostart=true tells the manager to walk map_server through configure -> activate for us.
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'bond_timeout': 0.0,
                     'node_names': ['map_server']}])

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Full path to the map YAML file to load'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo /clock instead of wall time'),
        map_server,
        lifecycle_manager,
    ])
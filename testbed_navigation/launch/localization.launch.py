#!/usr/bin/env python3
# Step 5: localization. This brings up map_server (so AMCL has a map to match against)
# plus AMCL itself, and hands both to one lifecycle_manager.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')

    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'),
        'maps', 'testbed_world.yaml')
    default_amcl = os.path.join(nav_pkg, 'config', 'amcl_params.yaml')

    map_yaml = LaunchConfiguration('map')
    amcl_params = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'yaml_filename': map_yaml}])

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params])

    # Order matters in node_names: map_server comes up before AMCL needs the map.
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'bond_timeout': 0.0,
                     'node_names': ['map_server', 'amcl']}])

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Full path to the map YAML file'),
        DeclareLaunchArgument('params_file', default_value=default_amcl,
                              description='Full path to the AMCL params file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo /clock instead of wall time'),
        map_server,
        amcl,
        lifecycle_manager,
    ])
#!/usr/bin/env python3
"""Step 1 - Map loading.

Starts the nav2 `map_server` (nav2_map_server) with the testbed map and a
dedicated lifecycle manager that configures + activates it.  Once active,
the occupancy grid is published (transient-local) on /map in the `map` frame.

    ros2 launch testbed_navigation map_loader.launch.py
    ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/other_map.yaml
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('testbed_bringup')
    nav_dir = get_package_share_directory('testbed_navigation')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('map_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(bringup_dir, 'maps', 'testbed_world.yaml'),
        description='Full path to the map yaml file to load')
    declare_params = DeclareLaunchArgument(
        'map_params_file',
        default_value=os.path.join(nav_dir, 'config', 'map_server_params.yaml'),
        description='Full path to the map_server parameter file')
    declare_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use the Gazebo /clock')
    declare_autostart = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically configure + activate the map_server')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        # The yaml_filename launch argument overrides the one in the params file
        parameters=[params_file,
                    {'yaml_filename': map_yaml,
                     'use_sim_time': use_sim_time}])

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': autostart,
                     'node_names': ['map_server']}])

    return LaunchDescription([
        declare_map,
        declare_params,
        declare_sim_time,
        declare_autostart,
        map_server,
        lifecycle_manager,
    ])

#!/usr/bin/python3
"""
map_loader.launch.py
--------------------
Launches the nav2_map_server to load the pre-built testbed world map,
and a lifecycle_manager to bring it into the ACTIVE state automatically.

Usage:
  ros2 launch testbed_navigation map_loader.launch.py
  ros2 launch testbed_navigation map_loader.launch.py map:=/path/to/custom.yaml
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # Resolve the map YAML from testbed_bringup package share directory
    # (requires testbed_bringup to be built and sourced)
    pkg_testbed_bringup = get_package_share_directory('testbed_bringup')
    default_map_yaml = os.path.join(pkg_testbed_bringup, 'maps', 'testbed_world.yaml')

    return LaunchDescription([

        # Allow map path to be overridden at launch time
        DeclareLaunchArgument(
            name='map',
            default_value=default_map_yaml,
            description='Full path to the map YAML file'
        ),

        # map_server: reads the .yaml and .pgm and publishes /map topic
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'yaml_filename': LaunchConfiguration('map'),
            }]
        ),

        # lifecycle_manager: transitions map_server through configure -> activate
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['map_server'],
            }]
        ),
    ])

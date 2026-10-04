#!/usr/bin/env python3
"""Step 1 - load the map.

Starts nav2_map_server (a lifecycle node) and a lifecycle manager that
configures + activates it. The map is then published on /map
(transient-local QoS, so late subscribers such as RViz still get it).

    ros2 launch testbed_navigation map_loader.launch.py
    ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/other.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': ParameterValue(map_yaml, value_type=str),
            'use_sim_time': use_sim_time,
        }],
    )

    # The map_server is a *lifecycle* node: it does nothing until it is taken
    # through configure -> activate. The lifecycle manager does that for us.
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

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Absolute path to the map yaml file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo /clock'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Automatically configure + activate the nodes'),
        map_server,
        lifecycle_manager,
    ])

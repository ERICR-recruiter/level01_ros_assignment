#!/usr/bin/env python3
"""Step 1 of the manual Nav2 workflow: load the static map.

Starts nav2_map_server/map_server (a lifecycle node) and a lifecycle_manager
that configures + activates it. The map is published on /map (latched,
transient_local) in the 'map' frame.

    ros2 launch testbed_navigation map_loader.launch.py
    ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/map.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'yaml_filename': map_yaml,
                     'topic_name': 'map',
                     'frame_id': 'map'}],
    )

    # map_server is a lifecycle node: it does nothing until someone
    # configures and activates it. lifecycle_manager does that for us.
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['map_server']}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Full path to the map yaml file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use Gazebo /clock'),
        map_server,
        lifecycle_manager,
    ])

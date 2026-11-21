#!/usr/bin/python3
"""
localization.launch.py
-----------------------
Launches map_server + AMCL for the testbed robot.
AMCL uses the robot's /scan topic (LaserScan, 300 rays, 0.1–1.5m range)
and the differential drive odometry (/odom) to localize in the loaded map.

Robot initial pose: x=0.0, y=5.0 (matches spawn_testbed.launch.py)

Usage:
  ros2 launch testbed_navigation localization.launch.py
  ros2 launch testbed_navigation localization.launch.py map:=/path/to/map.yaml
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_testbed_bringup    = get_package_share_directory('testbed_bringup')
    pkg_testbed_navigation = get_package_share_directory('testbed_navigation')

    default_map_yaml  = os.path.join(pkg_testbed_bringup,    'maps',   'testbed_world.yaml')
    default_amcl_yaml = os.path.join(pkg_testbed_navigation, 'config', 'amcl_params.yaml')

    return LaunchDescription([

        DeclareLaunchArgument(
            name='map',
            default_value=default_map_yaml,
            description='Full path to the map YAML file'
        ),

        DeclareLaunchArgument(
            name='params_file',
            default_value=default_amcl_yaml,
            description='Full path to the AMCL parameter file'
        ),

        # map_server: publishes /map
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

        # amcl: Monte Carlo localization — subscribes to /scan + /odom,
        # publishes /amcl_pose and the map->odom transform
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[LaunchConfiguration('params_file')]
        ),

        # lifecycle_manager: activates both map_server and amcl
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['map_server', 'amcl'],
            }]
        ),
    ])

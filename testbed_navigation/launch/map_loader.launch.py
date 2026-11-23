#!/usr/bin/env python3
"""Map loader launch file for Testbed robot.

Directly manages the map_server plugin via nav2_map_server and transitions
its lifecycle via nav2_lifecycle_manager without using nav2_bringup.
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

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(bringup_pkg, 'maps', 'testbed_world.yaml'),
        description='Full path to map yaml file to load')

    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(nav_pkg, 'config', 'map_server_params.yaml'),
        description='Full path to parameter file for map_server')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 lifecycle stack')

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {
                'yaml_filename': ParameterValue(map_yaml, value_type=str),
                'use_sim_time': use_sim_time,
            },
        ],
    )

    lifecycle_manager_node = Node(
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
        declare_map,
        declare_params,
        declare_use_sim_time,
        declare_autostart,
        map_server_node,
        lifecycle_manager_node,
    ])

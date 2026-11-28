#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    bringup_share = get_package_share_directory('testbed_bringup')
    nav_share = get_package_share_directory('testbed_navigation')

    default_map = os.path.join(bringup_share, 'maps', 'testbed_world.yaml')
    default_params = os.path.join(nav_share, 'config', 'map_server_params.yaml')

    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    sim_time_param = {'use_sim_time': ParameterValue(use_sim_time, value_type=bool)}

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=default_map,
            description='Absolute path to the occupancy grid map YAML file',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Absolute path to map_server parameter YAML file',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true',
        ),
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[
                params_file,
                sim_time_param,
                {'yaml_filename': map_file},
            ],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            output='screen',
            parameters=[
                params_file,
                sim_time_param,
                {
                    'autostart': True,
                    'node_names': ['map_server'],
                },
            ],
        ),
    ])

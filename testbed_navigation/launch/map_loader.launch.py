#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # 1. Declare Launch Arguments (matching nav2_bringup localization arguments)
    map_yaml_arg = DeclareLaunchArgument(
        'map',
        default_value='/media/subham/85dce0f4-2e29-4540-9a32-801850cfcef6/subham/ERIC_ROBOTICS/src/level01_ros_assignment/testbed_bringup/maps/testbed_world.yaml',
        description='Full path to map yaml file to load'
    )

    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value='/media/subham/85dce0f4-2e29-4540-9a32-801850cfcef6/subham/ERIC_ROBOTICS/src/level01_ros_assignment/testbed_navigation/config/amcl.yaml',
        description='Full path to the ROS2 parameters file to use for all launched nodes'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='True',
        description='Use simulation (Gazebo) clock if true'
    )

    # 2. Map LaunchConfigurations
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # 3. Nodes Configuration
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
                'yaml_filename': map_yaml,
            }
        ],
    )

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            params_file,
            {'use_sim_time': use_sim_time}
        ],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': ['map_server', 'amcl'],
            }
        ],
    )

    return LaunchDescription([
        map_yaml_arg,
        params_file_arg,
        use_sim_time_arg,
        map_server_node,
        amcl_node,
        lifecycle_manager,
    ])
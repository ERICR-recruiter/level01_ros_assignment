#!/usr/bin/env python3
"""Step 2 of the manual Nav2 workflow: localization with AMCL.

Includes map_loader.launch.py (map_server) and starts nav2_amcl/amcl with its
own lifecycle_manager. AMCL subscribes to /map + /scan + TF(odom->base_footprint)
and publishes TF map->odom and /amcl_pose.

    ros2 launch testbed_navigation localization.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('testbed_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    amcl_params = LaunchConfiguration('amcl_params')
    load_map = LaunchConfiguration('load_map')

    # Step 1: map_server (can be skipped with load_map:=false if it is already running)
    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_nav, 'launch', 'map_loader.launch.py')),
        launch_arguments={'map': LaunchConfiguration('map'),
                          'use_sim_time': use_sim_time}.items(),
        condition=IfCondition(load_map),
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params, {'use_sim_time': use_sim_time}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['amcl']}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('load_map', default_value='true',
                              description='Also start map_loader.launch.py'),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(get_package_share_directory('testbed_bringup'),
                                       'maps', 'testbed_world.yaml')),
        DeclareLaunchArgument(
            'amcl_params',
            default_value=os.path.join(pkg_nav, 'config', 'amcl_params.yaml')),
        map_loader,
        amcl,
        lifecycle_manager,
    ])

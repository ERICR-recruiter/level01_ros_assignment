#!/usr/bin/env python3
"""Step 2 - Localization.

Starts nav2 `amcl` (nav2_amcl) with testbed_navigation/config/amcl_params.yaml
and a dedicated lifecycle manager.  AMCL subscribes to /map (from
map_loader.launch.py), /scan and the odom -> base_footprint TF, and publishes
the map -> odom transform plus /amcl_pose and /particle_cloud.

    ros2 launch testbed_navigation localization.launch.py

Set `with_map:=true` to also start the map server from this launch file.
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
    nav_dir = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('amcl_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    with_map = LaunchConfiguration('with_map')

    declare_params = DeclareLaunchArgument(
        'amcl_params_file',
        default_value=os.path.join(nav_dir, 'config', 'amcl_params.yaml'),
        description='Full path to the AMCL parameter file')
    declare_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use the Gazebo /clock')
    declare_autostart = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically configure + activate AMCL')
    declare_with_map = DeclareLaunchArgument(
        'with_map', default_value='false',
        description='Also include map_loader.launch.py')

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_dir, 'launch', 'map_loader.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time,
                          'autostart': autostart}.items(),
        condition=IfCondition(with_map))

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}])

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': autostart,
                     'node_names': ['amcl']}])

    return LaunchDescription([
        declare_params,
        declare_sim_time,
        declare_autostart,
        declare_with_map,
        map_loader,
        amcl,
        lifecycle_manager,
    ])

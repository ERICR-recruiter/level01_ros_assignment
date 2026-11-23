#!/usr/bin/env python3
"""Full navigation bringup launch file for Testbed robot.

Combines the modular launch files:
  1. map_loader.launch.py      (Loads map via nav2_map_server)
  2. localization.launch.py    (Localizes robot via nav2_amcl)
  3. navigation.launch.py      (Nav2 planner, controller, behaviors, bt_navigator)
  4. rviz2                     (Navigation-focused RViz layout)

Usage:
  ros2 launch testbed_navigation full_navigation.launch.py
  ros2 launch testbed_navigation full_navigation.launch.py rviz:=false
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
    nav_pkg = get_package_share_directory('testbed_navigation')
    launch_dir = os.path.join(nav_pkg, 'launch')

    use_sim_time = LaunchConfiguration('use_sim_time')
    open_rviz = LaunchConfiguration('rviz')
    rviz_config = LaunchConfiguration('rvizconfig')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_open_rviz = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz2 with navigation layout')

    declare_rviz_config = DeclareLaunchArgument(
        'rvizconfig',
        default_value=os.path.join(nav_pkg, 'rviz', 'navigation.rviz'),
        description='Full path to RViz configuration file')

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, 'map_loader.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, 'localization.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, 'navigation.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_navigation',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(open_rviz),
        output='screen',
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_open_rviz,
        declare_rviz_config,
        map_loader,
        localization,
        navigation,
        rviz_node,
    ])

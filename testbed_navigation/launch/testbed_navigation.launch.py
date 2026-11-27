#!/usr/bin/env python3
"""Convenience launch: map_loader + localization + navigation (+ RViz).

Run the simulation first in another terminal:

    ros2 launch testbed_bringup testbed_full_bringup.launch.py

then:

    ros2 launch testbed_navigation testbed_navigation.launch.py

Each step can also be started on its own, in this order:
map_loader.launch.py -> localization.launch.py -> navigation.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    bringup_dir = get_package_share_directory('testbed_bringup')
    launch_dir = os.path.join(nav_dir, 'launch')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('rviz')

    args = [
        DeclareLaunchArgument(
            'map', default_value=os.path.join(bringup_dir, 'maps', 'testbed_world.yaml'),
            description='Full path to the map yaml file'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Start RViz with the navigation layout'),
        DeclareLaunchArgument('nav_delay', default_value='8.0',
                              description='Seconds to wait before starting the nav2 servers'),
    ]

    def include(name, extra=None):
        launch_args = {'use_sim_time': use_sim_time}
        launch_args.update(extra or {})
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, name)),
            launch_arguments=launch_args.items())

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_navigation',
        output='screen',
        arguments=['-d', os.path.join(nav_dir, 'rviz', 'navigation.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz))

    return LaunchDescription(args + [
        include('map_loader.launch.py', {'map': map_yaml}),
        include('localization.launch.py'),
        # Start the nav2 servers only once the map and AMCL (map->odom) are up,
        # i.e. the same order as running the three launch files by hand.
        TimerAction(period=LaunchConfiguration('nav_delay'),
                    actions=[include('navigation.launch.py')]),
        rviz,
    ])

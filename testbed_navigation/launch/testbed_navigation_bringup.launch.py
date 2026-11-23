#!/usr/bin/env python3
"""Convenience launch: simulation + map + localization + navigation + RViz.

Each stage is still its own launch file; this only chains them:

    testbed_bringup/testbed_full_bringup.launch.py   (Gazebo + robot, optional)
    map_loader.launch.py  -> localization.launch.py  -> navigation.launch.py
    rviz2 with the Nav2 panel

    ros2 launch testbed_navigation testbed_navigation_bringup.launch.py
    ros2 launch testbed_navigation testbed_navigation_bringup.launch.py sim:=false
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            TimerAction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    gazebo_dir = get_package_share_directory('testbed_gazebo')
    desc_dir = get_package_share_directory('testbed_description')
    launch_dir = os.path.join(nav_dir, 'launch')

    sim = LaunchConfiguration('sim')
    rviz = LaunchConfiguration('rviz')
    map_yaml = LaunchConfiguration('map')

    def include(path, condition=None, **args):
        return IncludeLaunchDescription(PythonLaunchDescriptionSource(path),
                                        condition=condition,
                                        launch_arguments=args.items())

    # Simulation (Gazebo + robot_state_publisher + spawn), without the
    # bringup's own odom-frame RViz - we start a Nav2 RViz below instead.
    simulation = [
        include(os.path.join(desc_dir, 'launch', 'robot_description.launch.py'),
                condition=IfCondition(sim), use_sim_time='true'),
        include(os.path.join(gazebo_dir, 'launch', 'spawn_playground.launch.py'),
                condition=IfCondition(sim)),
        include(os.path.join(gazebo_dir, 'launch', 'spawn_testbed.launch.py'),
                condition=IfCondition(sim)),
    ]

    localization = include(os.path.join(launch_dir, 'localization.launch.py'),
                           map=map_yaml, load_map='true')
    navigation = include(os.path.join(launch_dir, 'navigation.launch.py'))

    rviz_node = Node(
        package='rviz2', executable='rviz2', name='rviz2', output='log',
        condition=IfCondition(rviz),
        parameters=[{'use_sim_time': True}],
        arguments=['-d', os.path.join(nav_dir, 'rviz', 'testbed_navigation.rviz')])

    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='true',
                              description='Also start Gazebo and spawn the robot'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(get_package_share_directory('testbed_bringup'),
                                       'maps', 'testbed_world.yaml')),
        *simulation,
        # give Gazebo a few seconds to spawn the robot (odom TF + /scan) first
        TimerAction(period=5.0, actions=[localization, navigation, rviz_node]),
    ])

"""Convenience launch - everything in one go.

    gazebo + robot (testbed_bringup) -> map_loader -> localization -> navigation

It only includes the three step-by-step launch files, so nothing is configured here
that isn't in those. For debugging it's nicer to run them in separate terminals
(see the README).

    ros2 launch testbed_navigation testbed_navigation.launch.py
    ros2 launch testbed_navigation testbed_navigation.launch.py sim:=false   # sim already running
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    bringup_dir = get_package_share_directory('testbed_bringup')

    sim = LaunchConfiguration('sim')
    map_yaml = LaunchConfiguration('map')

    def include(pkg_dir, name, args=None, **kw):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', name)),
            launch_arguments=(args or {}).items(), **kw)

    simulation = include(
        bringup_dir, 'testbed_full_bringup.launch.py',
        {'rvizconfig': os.path.join(nav_dir, 'rviz', 'navigation.rviz')},
        condition=IfCondition(sim))

    map_loader = include(nav_dir, 'map_loader.launch.py', {'map': map_yaml})
    localization = include(nav_dir, 'localization.launch.py')
    navigation = include(nav_dir, 'navigation.launch.py')

    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='true',
                              description='Also start gazebo + rviz from testbed_bringup'),
        DeclareLaunchArgument(
            'map', default_value=os.path.join(bringup_dir, 'maps', 'testbed_world.yaml')),
        simulation,
        # give gazebo a few seconds to spawn the robot and start /clock,
        # otherwise AMCL and the costmaps spam TF warnings while they wait
        TimerAction(period=5.0, actions=[map_loader, localization]),
        TimerAction(period=8.0, actions=[navigation]),
    ])

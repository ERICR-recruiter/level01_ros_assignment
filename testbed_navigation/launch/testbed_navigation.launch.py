#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_testbed_navigation = get_package_share_directory('testbed_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    amcl_params_file = LaunchConfiguration('amcl_params_file')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(
            get_package_share_directory('testbed_bringup'),
            'maps',
            'testbed_world.yaml'
        ),
        description='Full path to map file to load'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(
            pkg_testbed_navigation,
            'config',
            'nav2_params.yaml'
        ),
        description='Full path to navigation parameters file'
    )

    declare_amcl_params_file_cmd = DeclareLaunchArgument(
        'amcl_params_file',
        default_value=os.path.join(
            pkg_testbed_navigation,
            'config',
            'amcl_params.yaml'
        ),
        description='Full path to AMCL localization parameters file'
    )

    map_loader_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_testbed_navigation, 'launch', 'map_loader.launch.py')
                ),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'map': map_yaml_file,
                    'autostart': autostart
                }.items()
            )
        ],
        scoped=True
    )

    # Explicitly pass amcl_params_file so parent params_file (nav2_params.yaml)
    # does not override child AMCL configuration
    localization_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_testbed_navigation, 'launch', 'localization.launch.py')
                ),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'autostart': autostart,
                    'params_file': amcl_params_file
                }.items()
            )
        ],
        scoped=True
    )

    navigation_group = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_testbed_navigation, 'launch', 'navigation.launch.py')
                ),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'params_file': params_file,
                    'autostart': autostart
                }.items()
            )
        ],
        scoped=True
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_amcl_params_file_cmd)
    ld.add_action(map_loader_group)
    ld.add_action(localization_group)
    ld.add_action(navigation_group)

    return ld

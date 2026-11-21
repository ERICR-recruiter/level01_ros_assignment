#!/usr/bin/python3
"""
navigation.launch.py — Full Nav2 navigation stack for Testbed-T1.0.0
Uses ParameterFile (Humble best practice) for reliable parameter loading.
Chains localization.launch.py so one command brings up everything.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile


def generate_launch_description():

    pkg_testbed_bringup    = get_package_share_directory('testbed_bringup')
    pkg_testbed_navigation = get_package_share_directory('testbed_navigation')

    default_map_yaml  = os.path.join(pkg_testbed_bringup,    'maps',   'testbed_world.yaml')
    default_nav2_yaml = os.path.join(pkg_testbed_navigation, 'config', 'nav2_params.yaml')
    default_amcl_yaml = os.path.join(pkg_testbed_navigation, 'config', 'amcl_params.yaml')

    # ParameterFile ensures correct YAML loading in ROS2 Humble
    # (avoids parameter namespace issues with sub-nodes like costmaps)
    nav2_params = ParameterFile(LaunchConfiguration('params_file'), allow_substs=True)

    # Reuse localization launch (map_server + amcl + their lifecycle manager)
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_navigation, 'launch', 'localization.launch.py')
        ),
        launch_arguments={
            'map':         LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('localization_params'),
        }.items()
    )

    return LaunchDescription([

        DeclareLaunchArgument('map',
            default_value=default_map_yaml,
            description='Full path to the map YAML file'),

        DeclareLaunchArgument('params_file',
            default_value=default_nav2_yaml,
            description='Full path to nav2 parameter file'),

        DeclareLaunchArgument('localization_params',
            default_value=default_amcl_yaml,
            description='Full path to AMCL parameter file'),

        # --- Localization stack (map_server + amcl) ---
        localization_launch,

        # --- Controller Server (DWB local planner) ---
        Node(
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[nav2_params],
            remappings=[('cmd_vel', 'cmd_vel')]
        ),

        # --- Planner Server (NavFn global planner) ---
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_params]
        ),

        # --- Behavior Server (spin, back_up, wait) ---
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_params]
        ),

        # --- BT Navigator ---
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_params]
        ),

        # --- Velocity Smoother ---
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[nav2_params]
        ),

        # --- Navigation Lifecycle Manager ---
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': [
                    'controller_server',
                    'planner_server',
                    'behavior_server',
                    'bt_navigator',
                    'velocity_smoother',
                ],
            }]
        ),
    ])

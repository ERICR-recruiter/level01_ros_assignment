#!/usr/bin/python3
"""
navigation.launch.py — Full Nav2 navigation stack for Testbed-T1.0.0
Uses direct resolved YAML path for reliable parameter loading.
Chains localization.launch.py so one command brings up everything.

FIX: Pass nav2_params_yaml as a resolved string (not LaunchConfiguration
substitution) so DWB can read critics at node startup time.
Also pass FollowPath.critics explicitly as a Python dict override to
guarantee DWB finds them regardless of YAML parser behavior.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_testbed_bringup    = get_package_share_directory('testbed_bringup')
    pkg_testbed_navigation = get_package_share_directory('testbed_navigation')

    # Resolve paths at description-generation time (not via LaunchConfiguration
    # substitution) so all nodes see absolute string paths immediately.
    default_map_yaml  = os.path.join(pkg_testbed_bringup,    'maps',   'testbed_world.yaml')
    default_nav2_yaml = os.path.join(pkg_testbed_navigation, 'config', 'nav2_params.yaml')
    default_amcl_yaml = os.path.join(pkg_testbed_navigation, 'config', 'amcl_params.yaml')

    # DWB critics explicitly declared as a Python dict override.
    # This guarantees the controller_server receives 'FollowPath.critics'
    # even if the YAML parameter file has loading order issues in Humble.
    dwb_critics_override = {
        'FollowPath.critics': [
            'RotateToGoal', 'Oscillation', 'BaseObstacle',
            'GoalAlign', 'PathAlign', 'PathDist', 'GoalDist',
        ],
    }

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
            description='Full path to nav2 parameter file (unused, kept for CLI compat)'),

        DeclareLaunchArgument('localization_params',
            default_value=default_amcl_yaml,
            description='Full path to AMCL parameter file'),

        # --- Localization stack (map_server + amcl) ---
        localization_launch,

        # --- Controller Server (DWB local planner) ---
        # Pass YAML file first, then dict override to guarantee critics are set.
        Node(
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[default_nav2_yaml, dwb_critics_override],
            remappings=[('cmd_vel', 'cmd_vel')]
        ),

        # --- Planner Server (NavFn global planner) ---
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[default_nav2_yaml]
        ),

        # --- Behavior Server (spin, back_up, wait) ---
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[default_nav2_yaml]
        ),

        # --- BT Navigator ---
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[default_nav2_yaml]
        ),

        # --- Velocity Smoother ---
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[default_nav2_yaml]
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

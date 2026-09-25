#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_share = get_package_share_directory('testbed_navigation')
    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')
    default_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    default_rviz = os.path.join(pkg_share, 'rviz', 'testbed_navigation.rviz')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('nav2_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    with_localization = LaunchConfiguration('with_localization')
    use_rviz = LaunchConfiguration('rviz')

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites={'use_sim_time': use_sim_time},
        convert_types=True)

    tf_remap = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    to_smoother = tf_remap + [('cmd_vel', 'cmd_vel_nav')]

    managed_nodes = [
        'controller_server',
        'smoother_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'velocity_smoother',
    ]

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'localization.launch.py')),
        condition=IfCondition(with_localization),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
        }.items())

    return LaunchDescription([
        DeclareLaunchArgument(
            'map', default_value=default_map,
            description='Map forwarded to localization.launch.py'),
        DeclareLaunchArgument(
            'nav2_params_file', default_value=default_params,
            description='Parameter file for the navigation servers'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the /clock published by Gazebo'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Let the lifecycle manager configure and activate the servers'),
        DeclareLaunchArgument(
            'with_localization', default_value='true',
            description='Also start map_server and AMCL'),
        DeclareLaunchArgument(
            'rviz', default_value='true',
            description='Start RViz with the navigation view'),
        DeclareLaunchArgument(
            'rviz_config', default_value=default_rviz,
            description='RViz configuration file'),

        localization,

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[configured_params],
            remappings=to_smoother),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[configured_params],
            remappings=tf_remap),

        Node(
            package='nav2_smoother',
            executable='smoother_server',
            name='smoother_server',
            output='screen',
            parameters=[configured_params],
            remappings=tf_remap),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[configured_params],
            remappings=to_smoother),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[configured_params],
            remappings=tf_remap),

        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[configured_params],
            remappings=tf_remap + [('cmd_vel', 'cmd_vel_nav'),
                                   ('cmd_vel_smoothed', 'cmd_vel')]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'autostart': autostart,
                         'node_names': managed_nodes}]),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            condition=IfCondition(use_rviz),
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-d', LaunchConfiguration('rviz_config')]),
    ])

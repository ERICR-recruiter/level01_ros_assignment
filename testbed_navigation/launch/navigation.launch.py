#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_testbed_nav = get_package_share_directory('testbed_navigation')
    default_params_file = os.path.join(pkg_testbed_nav, 'config', 'nav2_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')

    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator'
    ]

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to the ROS2 parameters file to use for all navigation nodes')

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack')

    # 1. Controller Server
    start_controller_server_cmd = Node(
        package='nav2_controller',
        executable='controller_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=[('cmd_vel', 'cmd_vel')]
    )

    # 2. Planner Server
    start_planner_server_cmd = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
    )

    # 3. Behavior Server (spin, backup, wait)
    start_behavior_server_cmd = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=[('cmd_vel', 'cmd_vel')]
    )

    # 4. BT Navigator
    start_bt_navigator_cmd = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=[('goal_pose', 'goal_pose_map')]
    )

    # 4b. Goal Pose Frame Relay (transforms RViz /goal_pose from odom to map)
    start_goal_relay_cmd = Node(
        package='testbed_navigation',
        executable='goal_pose_relay.py',
        name='goal_pose_relay',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 5. Lifecycle Manager for Navigation Nodes
    start_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': lifecycle_nodes
        }]
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_params_file_cmd,
        declare_autostart_cmd,
        start_controller_server_cmd,
        start_planner_server_cmd,
        start_behavior_server_cmd,
        start_bt_navigator_cmd,
        start_goal_relay_cmd,
        start_lifecycle_manager_cmd,
    ])

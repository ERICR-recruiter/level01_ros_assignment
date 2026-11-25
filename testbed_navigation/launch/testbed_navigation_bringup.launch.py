#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_testbed_nav = get_package_share_directory('testbed_navigation')
    pkg_testbed_bringup = get_package_share_directory('testbed_bringup')

    default_map_file = os.path.join(pkg_testbed_bringup, 'maps', 'testbed_world.yaml')
    default_amcl_params = os.path.join(pkg_testbed_nav, 'config', 'amcl_params.yaml')
    default_nav2_params = os.path.join(pkg_testbed_nav, 'config', 'nav2_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml_file = LaunchConfiguration('map')
    amcl_params_file = LaunchConfiguration('amcl_params')
    nav2_params_file = LaunchConfiguration('nav2_params')
    autostart = LaunchConfiguration('autostart')

    # Ordered lifecycle nodes to ensure dependencies are resolved:
    # 1. map_server provides /map
    # 2. amcl provides map -> odom TF
    # 3. controller_server initializes local costmap
    # 4. planner_server initializes global costmap (requires map TF)
    # 5. behavior_server initializes recoveries
    # 6. bt_navigator starts action coordinator
    lifecycle_nodes = [
        'map_server',
        'amcl',
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator'
    ]

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=default_map_file,
        description='Full path to map yaml file to load')

    declare_amcl_params_cmd = DeclareLaunchArgument(
        'amcl_params',
        default_value=default_amcl_params,
        description='Full path to the AMCL parameters file')

    declare_nav2_params_cmd = DeclareLaunchArgument(
        'nav2_params',
        default_value=default_nav2_params,
        description='Full path to the Nav2 parameters file')

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack')

    # 1. Map Server
    start_map_server_cmd = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'yaml_filename': map_yaml_file,
            'topic_name': 'map',
            'frame_id': 'map'
        }]
    )

    # 2. AMCL Localization
    start_amcl_cmd = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file, {'use_sim_time': use_sim_time}],
        remappings=[('/scan', 'scan')]
    )

    # 3. Controller Server
    start_controller_server_cmd = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params_file, {'use_sim_time': use_sim_time}],
        remappings=[('cmd_vel', 'cmd_vel')]
    )

    # 4. Planner Server
    start_planner_server_cmd = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params_file, {'use_sim_time': use_sim_time}],
    )

    # 5. Behavior Server
    start_behavior_server_cmd = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_params_file, {'use_sim_time': use_sim_time}],
        remappings=[('cmd_vel', 'cmd_vel')]
    )

    # 6. BT Navigator
    start_bt_navigator_cmd = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_params_file, {'use_sim_time': use_sim_time}],
        remappings=[('goal_pose', 'goal_pose_map')]
    )

    # 6b. Goal Pose Frame Relay (transforms RViz /goal_pose from odom to map)
    start_goal_relay_cmd = Node(
        package='testbed_navigation',
        executable='goal_pose_relay.py',
        name='goal_pose_relay',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 7. Coordinated Lifecycle Manager
    start_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': lifecycle_nodes,
            'bond_timeout': 10.0
        }]
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_map_yaml_cmd,
        declare_amcl_params_cmd,
        declare_nav2_params_cmd,
        declare_autostart_cmd,
        start_map_server_cmd,
        start_amcl_cmd,
        start_controller_server_cmd,
        start_planner_server_cmd,
        start_behavior_server_cmd,
        start_bt_navigator_cmd,
        start_goal_relay_cmd,
        start_lifecycle_manager_cmd,
    ])

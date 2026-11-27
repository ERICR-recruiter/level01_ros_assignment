#!/usr/bin/env python3
"""Step 3 - Navigation.

Starts each nav2 server individually (no nav2_bringup) with
testbed_navigation/config/nav2_params.yaml:

    planner_server     global path         (NavFn)
    controller_server  path following      (Regulated Pure Pursuit)
    behavior_server    recoveries          (Spin, BackUp, Wait, DriveOnHeading)
    bt_navigator       NavigateToPose action server running the behaviour tree
    velocity_smoother  cmd_vel_nav      -> cmd_vel_smoothed
    collision_monitor  cmd_vel_smoothed -> cmd_vel

plus one lifecycle manager that brings them up in order.  Requires the map
(map_loader.launch.py) and localization (localization.launch.py) to run.

    ros2 launch testbed_navigation navigation.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('nav2_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_params = DeclareLaunchArgument(
        'nav2_params_file',
        default_value=os.path.join(nav_dir, 'config', 'nav2_params.yaml'),
        description='Full path to the nav2 parameter file')
    declare_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use the Gazebo /clock')
    declare_autostart = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically configure + activate the nav2 servers')

    # Order matters: the lifecycle manager activates nodes in this order and
    # bt_navigator needs the action servers of the others to exist.
    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'velocity_smoother',
        'collision_monitor',
    ]

    common = [params_file, {'use_sim_time': use_sim_time}]

    # Like nav2_bringup, no `name=` here: the executable already names the
    # node 'controller_server' (and also creates the local_costmap node).
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        output='screen',
        parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav')])

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=common)

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav')])

    bt_dir = os.path.join(nav_dir, 'behavior_trees')
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=common + [{
            'default_nav_to_pose_bt_xml':
                os.path.join(bt_dir, 'navigate_to_pose_w_replanning_and_recovery.xml'),
            'default_nav_through_poses_bt_xml':
                os.path.join(bt_dir, 'navigate_through_poses_w_replanning_and_recovery.xml'),
        }])

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav'),
                    ('cmd_vel_smoothed', 'cmd_vel_smoothed')])

    collision_monitor = Node(
        package='nav2_collision_monitor',
        executable='collision_monitor',
        name='collision_monitor',
        output='screen',
        parameters=common)

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': autostart,
                     'node_names': lifecycle_nodes}])

    return LaunchDescription([
        # Print log lines as they come (helps when several nodes share a terminal)
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),
        declare_params,
        declare_sim_time,
        declare_autostart,
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        velocity_smoother,
        collision_monitor,
        lifecycle_manager,
    ])

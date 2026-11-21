#!/usr/bin/env python3
"""
Brings up the Nav2 navigation servers for Testbed-T1.0.0, one node at a time
(instead of nav2_bringup):

  planner_server    -> NavFn global planner
  controller_server -> DWB local planner   (publishes /cmd_vel_nav)
  behavior_server   -> spin / backup / drive_on_heading / wait recoveries
  bt_navigator      -> NavigateToPose behaviour tree
  velocity_smoother -> /cmd_vel_nav  ->  /cmd_vel  (to the Gazebo diff-drive plugin)
  lifecycle_manager_navigation -> configures + activates all of the above

Run map_loader.launch.py and localization.launch.py first.
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_params = os.path.join(
        get_package_share_directory('testbed_navigation'), 'config', 'nav2_params.yaml')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    common_params = [params_file, {'use_sim_time': use_sim_time}]

    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'velocity_smoother',
    ]

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=common_params,
        # Controller output goes to the smoother, not straight to the robot
        remappings=[('cmd_vel', 'cmd_vel_nav')],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=common_params,
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=common_params,
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=common_params,
    )

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=common_params,
        remappings=[('cmd_vel', 'cmd_vel_nav'),          # input  (from controller)
                    ('cmd_vel_smoothed', 'cmd_vel')],    # output (to diff-drive plugin)
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': lifecycle_nodes,
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=default_params,
                              description='Full path to the Nav2 parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use Gazebo /clock'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Automatically configure and activate the Nav2 servers'),
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        velocity_smoother,
        lifecycle_manager,
    ])

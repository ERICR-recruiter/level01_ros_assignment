#!/usr/bin/env python3
"""Step 3 - navigate.

Starts the Nav2 servers one by one (no nav2_bringup):

  controller_server  local planner (DWB) + local costmap     -> action /follow_path
  planner_server     global planner (NavFn) + global costmap -> action /compute_path_to_pose
  behavior_server    recoveries: spin, backup, wait          -> actions /spin /backup ...
  bt_navigator       behaviour tree that glues the above     -> action /navigate_to_pose

plus a lifecycle manager that brings them all up. Needs /map (map_loader) and
the map -> odom transform (localization) to be running.

    ros2 launch testbed_navigation navigation.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites={'use_sim_time': use_sim_time},
        convert_types=True)

    # Order matters for the lifecycle manager: it starts nodes in this order and
    # shuts them down in reverse order.
    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
    ]

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[configured_params],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[configured_params],
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[configured_params],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[configured_params],
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
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg, 'config', 'nav2_params.yaml'),
            description='Nav2 parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo /clock'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Automatically configure + activate the nodes'),
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        lifecycle_manager,
    ])

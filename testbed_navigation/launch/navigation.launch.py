#!/usr/bin/env python3
"""Manual Navigation launch file for Testbed robot.

Manually starts Nav2 core components:
  * controller_server (DWB Local Planner & Local Costmap)
  * planner_server (Navfn Global Planner & Global Costmap)
  * behavior_server (Recovery behaviors: Spin, Backup, Wait, DriveOnHeading)
  * bt_navigator (Behavior Tree Navigator providing NavigateToPose action)
  * lifecycle_manager_navigation (transitions the above lifecycle nodes in order)
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_pkg = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(nav_pkg, 'config', 'nav2_params.yaml'),
        description='Full path to parameter file for Nav2 servers')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 lifecycle stack')

    common_params = [params_file, {'use_sim_time': use_sim_time}]

    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        respawn=False,
        parameters=common_params,
    )

    planner_server_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        respawn=False,
        parameters=common_params,
    )

    behavior_server_node = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        respawn=False,
        parameters=common_params,
    )

    bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        respawn=False,
        parameters=common_params,
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': [
                'controller_server',
                'planner_server',
                'behavior_server',
                'bt_navigator',
            ],
        }],
    )

    return LaunchDescription([
        declare_params,
        declare_use_sim_time,
        declare_autostart,
        controller_server_node,
        planner_server_node,
        behavior_server_node,
        bt_navigator_node,
        lifecycle_manager_node,
    ])

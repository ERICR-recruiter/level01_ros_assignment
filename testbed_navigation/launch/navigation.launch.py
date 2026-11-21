#!/usr/bin/env python3
"""Step 3 of the manual Nav2 workflow: navigation servers (no nav2_bringup).

Nodes (Nav2 lifecycle nodes, switched on by one lifecycle_manager):
  planner_server    - global path (NavFn)
  controller_server - follows the path, publishes /cmd_vel (Regulated Pure Pursuit)
  behavior_server   - recoveries (spin / backup / wait)
  bt_navigator      - NavigateToPose action server, runs the behaviour tree

    ros2 launch testbed_navigation navigation.launch.py                     # nav servers only
    ros2 launch testbed_navigation navigation.launch.py localization:=true  # + map_server + AMCL
    ros2 launch testbed_navigation navigation.launch.py rviz:=false         # without the extra RViz
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('testbed_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params = [LaunchConfiguration('params_file'), {'use_sim_time': use_sim_time}]

    # optional: map_server + AMCL from the same terminal
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_nav, 'launch', 'localization.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
        condition=IfCondition(LaunchConfiguration('localization')),
    )

    nav_nodes = [
        Node(package='nav2_planner', executable='planner_server',
             name='planner_server', output='screen', parameters=params),
        Node(package='nav2_controller', executable='controller_server',
             name='controller_server', output='screen', parameters=params),
        Node(package='nav2_behaviors', executable='behavior_server',
             name='behavior_server', output='screen', parameters=params),
        Node(package='nav2_bt_navigator', executable='bt_navigator',
             name='bt_navigator', output='screen', parameters=params),
    ]

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['planner_server', 'controller_server',
                                    'behavior_server', 'bt_navigator']}],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_navigation',
        output='log',
        arguments=['-d', os.path.join(pkg_nav, 'rviz', 'navigation.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('localization', default_value='false',
                              description='Also start map_server + AMCL'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Open RViz with map, costmaps, particles, path'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_nav, 'config', 'nav2_params.yaml')),
        localization,
        *nav_nodes,
        lifecycle_manager,
        rviz,
    ])

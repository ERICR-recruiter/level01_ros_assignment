#!/usr/bin/env python3
"""Step 3 - Navigation.

Starts the Nav2 navigation servers individually, each loading its plugins from
config/nav2_params.yaml, and one lifecycle manager that brings them up in order:

    controller_server  - FollowPath (Regulated Pure Pursuit) + local costmap
    planner_server     - GridBased (NavFn) + global costmap
    behavior_server    - spin / backup / drive_on_heading / wait recoveries
    bt_navigator       - NavigateToPose / NavigateThroughPoses action servers
    velocity_smoother  - /cmd_vel_nav -> /cmd_vel

Requires map + localization to be running (localization.launch.py).

    ros2 launch testbed_navigation navigation.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('nav2_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    declare_args = [
        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=os.path.join(nav_share, 'config', 'nav2_params.yaml'),
            description='Nav2 navigation servers parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('log_level', default_value='info'),
    ]

    # Order matters: the lifecycle manager activates nodes in this order and
    # bt_navigator needs the other action servers to exist first.
    lifecycle_nodes = ['controller_server',
                       'planner_server',
                       'behavior_server',
                       'bt_navigator',
                       'velocity_smoother']

    common = [params_file, {'use_sim_time': use_sim_time}]
    ros_args = ['--ros-args', '--log-level', log_level]
    tf_remaps = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=common,
        arguments=ros_args,
        # controller output goes through the velocity smoother
        remappings=tf_remaps + [('cmd_vel', 'cmd_vel_nav')],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=common,
        arguments=ros_args,
        remappings=tf_remaps,
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=common,
        arguments=ros_args,
        remappings=tf_remaps,
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=common,
        arguments=ros_args,
        remappings=tf_remaps,
    )

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=common,
        arguments=ros_args,
        remappings=tf_remaps + [('cmd_vel', 'cmd_vel_nav'),
                                ('cmd_vel_smoothed', 'cmd_vel')],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': autostart,
                     'node_names': lifecycle_nodes}],
    )

    return LaunchDescription(declare_args + [
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        velocity_smoother,
        lifecycle_manager,
    ])

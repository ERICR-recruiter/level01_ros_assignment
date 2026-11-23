#!/usr/bin/env python3
"""Step 3 - Navigation.

Manually assembles the Nav2 navigation servers (instead of nav2_bringup):

    planner_server     (NavFn global planner + global_costmap)
    controller_server  (Regulated Pure Pursuit + local_costmap)
    behavior_server    (spin / backup / wait recoveries)
    bt_navigator       (NavigateToPose / NavigateThroughPoses actions)
    velocity_smoother  (cmd_vel_nav -> cmd_vel)
    lifecycle_manager_navigation

Requires a map -> odom -> base_footprint TF chain, i.e. run
localization.launch.py first (or together, see testbed_navigation_bringup).

    ros2 launch testbed_navigation navigation.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('nav2_params_file')
    bt_xml = LaunchConfiguration('bt_xml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    lifecycle_nodes = ['controller_server',
                       'planner_server',
                       'behavior_server',
                       'bt_navigator',
                       'velocity_smoother']

    configured_params = RewrittenYaml(
        source_file=params_file,
        param_rewrites={'use_sim_time': use_sim_time,
                        'default_nav_to_pose_bt_xml': bt_xml},
        convert_types=True)

    common = dict(output='screen',
                  respawn=False,
                  arguments=['--ros-args', '--log-level', log_level])

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),

        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=os.path.join(nav_dir, 'config', 'nav2_params.yaml'),
            description='Nav2 parameter file'),
        DeclareLaunchArgument(
            'bt_xml',
            default_value=os.path.join(nav_dir, 'behavior_trees',
                                       'navigate_to_pose_testbed.xml'),
            description='Behavior tree used for NavigateToPose'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('log_level', default_value='info'),

        Node(package='nav2_controller', executable='controller_server',
             parameters=[configured_params],
             # controller output goes through the velocity smoother
             remappings=[('cmd_vel', 'cmd_vel_nav')],
             **common),

        Node(package='nav2_planner', executable='planner_server',
             name='planner_server', parameters=[configured_params], **common),

        Node(package='nav2_behaviors', executable='behavior_server',
             name='behavior_server', parameters=[configured_params],
             remappings=[('cmd_vel', 'cmd_vel_nav')],
             **common),

        Node(package='nav2_bt_navigator', executable='bt_navigator',
             name='bt_navigator', parameters=[configured_params], **common),

        Node(package='nav2_velocity_smoother', executable='velocity_smoother',
             name='velocity_smoother', parameters=[configured_params],
             remappings=[('cmd_vel', 'cmd_vel_nav'),
                         ('cmd_vel_smoothed', 'cmd_vel')],
             **common),

        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_navigation', output='screen',
             parameters=[{'use_sim_time': use_sim_time},
                         {'autostart': autostart},
                         {'node_names': lifecycle_nodes}],
             arguments=['--ros-args', '--log-level', log_level]),
    ])

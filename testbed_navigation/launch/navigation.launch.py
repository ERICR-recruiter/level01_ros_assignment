"""Step 3 - the actual navigation servers.

planner_server, controller_server, behavior_server, bt_navigator and
velocity_smoother, all managed by one lifecycle manager.

cmd_vel path:
    controller_server --/cmd_vel_nav--> velocity_smoother --/cmd_vel--> gazebo diff drive

Run this after map_loader + localization (the costmaps wait for the map -> odom TF).

    ros2 launch testbed_navigation navigation.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    bt_xml = LaunchConfiguration('bt_xml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_args = [
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'nav2_params.yaml'),
            description='nav2 parameter file (planner, controller, costmaps, BT, ...)'),
        DeclareLaunchArgument(
            'bt_xml',
            default_value=os.path.join(nav_dir, 'behavior_trees', 'navigate_to_pose.xml'),
            description='Behavior tree used for NavigateToPose'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
    ]

    common = [params_file, {'use_sim_time': use_sim_time}]

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav')],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=common,
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=common,
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=common + [{'default_nav_to_pose_bt_xml': bt_xml}],
    )

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=common,
        remappings=[('cmd_vel', 'cmd_vel_nav'),
                    ('cmd_vel_smoothed', 'cmd_vel')],
    )

    # order matters a bit - the lifecycle manager brings them up in this order
    # and bt_navigator should come after the servers it talks to
    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'velocity_smoother',
    ]

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
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        velocity_smoother,
        lifecycle_manager,
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_params_file = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config',
        'nav2_params.yaml',
    )
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')

    navigation_nodes = [
        'planner_server',
        'controller_server',
        'behavior_server',
        'bt_navigator',
    ]

    return LaunchDescription([
        
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file,
            description='Path to the navigation parameters YAML file.',
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            choices=['true', 'false'],
            description='Automatically activate the navigation servers.',
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': autostart,
                'node_names': navigation_nodes,
            }],
        ),
    ])

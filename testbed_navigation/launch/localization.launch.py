#!/usr/bin/env python3
"""Step 2 - localize with AMCL.

Starts nav2_amcl and its own lifecycle manager. AMCL needs the map, so run
map_loader.launch.py first (or use testbed_nav_full.launch.py). It publishes
the map -> odom transform once it has an initial pose (set in amcl_params.yaml
to the robot's Gazebo spawn pose, or give one with RViz "2D Pose Estimate").

    ros2 launch testbed_navigation localization.launch.py
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

    # Lets the use_sim_time launch argument override the value inside the yaml.
    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key='',
        param_rewrites={'use_sim_time': use_sim_time},
        convert_types=True)

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[configured_params],
    )

    # Name matches what the Nav2 RViz panel expects (lifecycle_manager_localization).
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': ['amcl'],
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg, 'config', 'amcl_params.yaml'),
            description='AMCL parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo /clock'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Automatically configure + activate the nodes'),
        amcl,
        lifecycle_manager,
    ])

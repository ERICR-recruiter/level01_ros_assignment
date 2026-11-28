#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')
    pkg_testbed_description = get_package_share_directory('testbed_description')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    rvizconfig = LaunchConfiguration('rvizconfig')

    default_rviz_config = os.path.join(
        pkg_testbed_description,
        'rviz',
        'full_bringup.rviz',
    )

    state_pub = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_description, 'launch', 'robot_description.launch.py'),
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_gazebo, 'launch', 'spawn_playground.launch.py'),
        ),
    )

    # Delay spawning slightly so gzserver and /spawn_entity service are ready
    spawn = TimerAction(
        period=3.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_testbed_gazebo, 'launch', 'spawn_testbed.launch.py'),
                ),
            ),
        ],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        output='screen',
        condition=IfCondition(use_rviz),
        parameters=[{'use_sim_time': ParameterValue(use_sim_time, value_type=bool)}],
        arguments=['-d', rvizconfig],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz2 alongside Gazebo',
        ),
        DeclareLaunchArgument(
            'rvizconfig',
            default_value=default_rviz_config,
            description='Absolute path to RViz2 configuration file',
        ),
        state_pub,
        gazebo,
        spawn,
        rviz_node,
    ])
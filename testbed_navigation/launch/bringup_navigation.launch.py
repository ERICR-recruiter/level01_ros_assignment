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
    bringup_share = get_package_share_directory('testbed_bringup')
    nav_share = get_package_share_directory('testbed_navigation')

    default_map = os.path.join(bringup_share, 'maps', 'testbed_world.yaml')
    default_rviz = os.path.join(nav_share, 'rviz', 'nav2_view.rviz')

    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_share, 'launch', 'map_loader.launch.py'),
        ),
        launch_arguments={
            'map': map_file,
            'use_sim_time': use_sim_time,
        }.items(),
    )

    localization = TimerAction(
        period=2.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav_share, 'launch', 'localization.launch.py'),
                ),
                launch_arguments={'use_sim_time': use_sim_time}.items(),
            ),
        ],
    )

    navigation = TimerAction(
        period=4.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav_share, 'launch', 'navigation.launch.py'),
                ),
                launch_arguments={'use_sim_time': use_sim_time}.items(),
            ),
        ],
    )

    rviz_node = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2_navigation',
                output='screen',
                condition=IfCondition(use_rviz),
                parameters=[{'use_sim_time': ParameterValue(use_sim_time, value_type=bool)}],
                arguments=['-d', rviz_config],
            ),
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=default_map,
            description='Absolute path to the occupancy grid map YAML file',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz2 with the Nav2 visualization layout',
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=default_rviz,
            description='Absolute path to the RViz2 navigation config file',
        ),
        map_loader,
        localization,
        navigation,
        rviz_node,
    ])

"""Step 1 - load the static map.

Starts nav2's map_server and a lifecycle manager that configures + activates it.
After this the map is latched on /map (transient local), so anything started later
(AMCL, the global costmap, rviz) still gets it.

    ros2 launch testbed_navigation map_loader.launch.py
    ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/to/other_map.yaml
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    bringup_dir = get_package_share_directory('testbed_bringup')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_args = [
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_dir, 'maps', 'testbed_world.yaml'),
            description='Full path to the map yaml'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'map_server_params.yaml'),
            description='map_server parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='Configure + activate map_server right away'),
    ]

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        # yaml_filename comes after the params file so map:= always wins
        parameters=[params_file,
                    {'yaml_filename': map_yaml,
                     'use_sim_time': use_sim_time}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': autostart,
                     'node_names': ['map_server']}],
    )

    return LaunchDescription(declare_args + [map_server, lifecycle_manager])

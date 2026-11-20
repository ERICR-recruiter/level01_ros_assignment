import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')
    bringup_share = get_package_share_directory('testbed_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use Gazebo /clock'),
        DeclareLaunchArgument('map',
                              default_value=os.path.join(bringup_share, 'maps', 'testbed_world.yaml'),
                              description='Absolute path to the map yaml'),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(nav_share, 'config', 'map_server_params.yaml'),
                              description='map_server parameter file'),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[params_file,
                        {'yaml_filename': map_yaml, 'use_sim_time': use_sim_time}],
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'autostart': True,
                         'node_names': ['map_server']}],
        ),
    ])

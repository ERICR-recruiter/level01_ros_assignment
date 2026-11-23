from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'), 'config', 'map_params.yaml'
    ])
    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=PathJoinSubstitution([
            FindPackageShare('testbed_bringup'), 'maps', 'testbed_world.yaml'
        ])),
        Node(package='nav2_map_server', executable='map_server',
             name='map_server', output='screen', parameters=[params, {'yaml_filename': LaunchConfiguration('map')}]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_map_loader', output='screen', parameters=[{
                 'use_sim_time': True, 'autostart': True,
                 'bond_timeout': 30.0,
                 'node_names': ['map_server'],
             }]),
    ])

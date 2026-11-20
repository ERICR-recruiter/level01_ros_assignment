import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

pkg = get_package_share_directory('testbed_bringup')

ARGUMENTS = [
    DeclareLaunchArgument(
        'map_path',
        default_value=os.path.join(pkg, 'maps', 'testbed_world'),
        description='Saved map path WITHOUT extension (used for loading and autosave)')
]


def generate_launch_description():
    map_path = LaunchConfiguration('map_path')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': [map_path, '.yaml'],
            'use_sim_time': True
        }],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['map_server'],
            'use_sim_time': True
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(map_server)
    ld.add_action(lifecycle_manager)
    return ld
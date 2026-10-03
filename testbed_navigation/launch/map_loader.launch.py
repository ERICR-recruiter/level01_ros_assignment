import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    testbed_bringup_dir = get_package_share_directory('testbed_bringup')
    map_yaml_path = os.path.join(testbed_bringup_dir, 'maps', 'testbed_world.yaml')

    map_loader = Node(
        package = 'nav2_map_server',
        executable = 'map_server',
        name = 'map_server',
        output = 'screen',
        parameters = [{'yaml_filename' : map_yaml_path}]
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                    'map_server',
                ]
            }]
        )

    return LaunchDescription([
        map_loader,
        lifecycle_manager_node
    ])
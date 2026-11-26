import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    map_file = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')
    amcl_params = os.path.join(
        get_package_share_directory('testbed_navigation'), 'config', 'amcl_params.yaml')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map_file, 'use_sim_time': True}],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params],
    )

    # starts both nodes, in this order (map first, then amcl)
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': True,
                     'autostart': True,
                     'node_names': ['map_server', 'amcl']}],
    )

    return LaunchDescription([map_server, amcl, lifecycle_manager])

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    navigation_dir = get_package_share_directory('testbed_navigation')

    amcl_params_file = os.path.join(
        navigation_dir,
        'config',
        'amcl_params.yaml'
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['amcl']
        }]
    )

    return LaunchDescription([
        amcl,
        lifecycle_manager
    ])

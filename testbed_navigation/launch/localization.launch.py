import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    navigation_dir = get_package_share_directory(
        'testbed_navigation'
    )

    amcl_params = os.path.join(
        navigation_dir,
        'config',
        'amcl_params.yaml'
    )

    # AMCL Localization
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_params,
            {'use_sim_time': True}
        ]
    )

    # Lifecycle Manager for AMCL
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'autostart': True},
            {'node_names': ['amcl']}
        ]
    )

    return LaunchDescription([
        amcl_node,
        lifecycle_manager
    ])

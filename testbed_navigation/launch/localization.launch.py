import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    nav_pkg = get_package_share_directory('testbed_navigation')

    amcl_config = os.path.join(
        nav_pkg,
        'config',
        'amcl_params.yaml'
    )

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_config,
            {'use_sim_time': True}
        ]
    )

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

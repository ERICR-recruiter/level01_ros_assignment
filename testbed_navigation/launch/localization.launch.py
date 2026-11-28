import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_testbed_navigation = get_package_share_directory('testbed_navigation')
    amcl_params_file = os.path.join(pkg_testbed_navigation, 'config', 'amcl_params.yaml')

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file]
    )

    lifecycle_manager_node = Node(
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
        lifecycle_manager_node
    ])

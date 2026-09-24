import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Find the parameter file
    config_dir = os.path.join(get_package_share_directory('testbed_navigation'), 'config')
    amcl_config = os.path.join(config_dir, 'amcl_params.yaml')

    # AMCL Node
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_config]
    )

    # Lifecycle Manager for AMCL
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': True},
                    {'autostart': True},
                    {'node_names': ['amcl']}]
    )

    return LaunchDescription([
        amcl_node,
        lifecycle_manager_node
    ])

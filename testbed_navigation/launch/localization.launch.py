from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    params_file = os.path.join(nav_dir, 'config', 'amcl_params.yaml')

    return LaunchDescription([
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[params_file, {'use_sim_time': True}]
        ),
        Node(
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
    ])

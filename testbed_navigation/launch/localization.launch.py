from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'), 'config', 'amcl_params.yaml'
    ])
    return LaunchDescription([
        Node(package='nav2_amcl', executable='amcl',
             name='amcl', output='screen', parameters=[params]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_localization', output='screen', parameters=[{
                 'use_sim_time': True, 'autostart': True,
                 'bond_timeout': 30.0,
                 'node_names': ['amcl'],
             }]),
    ])

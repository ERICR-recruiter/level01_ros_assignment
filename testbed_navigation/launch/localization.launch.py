import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

pkg = get_package_share_directory('testbed_navigation')

ARGUMENTS = [

    DeclareLaunchArgument(
        'amcl_params_file',
        default_value=os.path.join(pkg, 'config', 'amcl_params.yaml'),
        description='Full path to the AMCL params file'),
]


def generate_launch_description():
    amcl_params_file = LaunchConfiguration('amcl_params_file')

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file, {'use_sim_time': True}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['amcl'],
            'use_sim_time': True
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(amcl)
    ld.add_action(lifecycle_manager)
    return ld
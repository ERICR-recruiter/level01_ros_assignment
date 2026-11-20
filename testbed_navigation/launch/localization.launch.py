import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('testbed_bringup')
    nav_dir = get_package_share_directory('testbed_navigation')

    default_map = os.path.join(bringup_dir, 'maps', 'testbed_world.yaml')
    default_params = os.path.join(nav_dir, 'config', 'amcl_params.yaml')

    map_arg = DeclareLaunchArgument('map', default_value=default_map)
    params_arg = DeclareLaunchArgument('params_file', default_value=default_params)
    sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': LaunchConfiguration('map'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[LaunchConfiguration('params_file')],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }],
    )

    return LaunchDescription([
        map_arg, params_arg, sim_time_arg,
        map_server, amcl, lifecycle_manager,
    ])

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_testbed_bringup = get_package_share_directory('testbed_bringup')
    pkg_testbed_nav = get_package_share_directory('testbed_navigation')

    default_map_path = os.path.join(pkg_testbed_bringup, 'maps', 'testbed_world.yaml')
    default_amcl_params = os.path.join(pkg_testbed_nav, 'config', 'amcl_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation clock if true'
    )
    declare_map = DeclareLaunchArgument(
        'map', default_value=default_map_path,
        description='Full path to map yaml file'
    )
    declare_params = DeclareLaunchArgument(
        'params_file', default_value=default_amcl_params,
        description='Full path to AMCL param file'
    )

    # 1. Map Server Node
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml_file,
            'use_sim_time': use_sim_time
        }]
    )

    # 2. AMCL Node
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]
    )

    # 3. Lifecycle Manager for both map_server and amcl
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_map,
        declare_params,
        map_server_node,
        amcl_node,
        lifecycle_manager_node
    ])
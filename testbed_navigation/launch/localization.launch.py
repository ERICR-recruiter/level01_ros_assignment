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

    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    amcl_params_file = LaunchConfiguration('params_file')

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to map yaml file to load'
    )

    declare_amcl_params_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_amcl_params,
        description='Full path to the AMCL configuration yaml file'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the localization nodes'
    )

    # Node: Map Server
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'yaml_filename': map_yaml_file
        }]
    )

    # Node: AMCL Localization
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file, {'use_sim_time': use_sim_time}],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
    )

    # Lifecycle Manager for Localization
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': ['map_server', 'amcl']
        }]
    )

    return LaunchDescription([
        declare_map_yaml_cmd,
        declare_amcl_params_cmd,
        declare_use_sim_time_cmd,
        declare_autostart_cmd,
        map_server_node,
        amcl_node,
        lifecycle_manager_node,
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg_bringup = get_package_share_directory('testbed_bringup')
    pkg_navigation = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)
    autostart = ParameterValue(LaunchConfiguration('autostart'), value_type=bool)

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
                'yaml_filename': LaunchConfiguration('map'),
            },
        ],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
                'autostart': autostart,
            },
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(pkg_bringup, 'maps', 'testbed_world.yaml'),
            description='Absolute path to the map yaml file'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_navigation, 'config', 'map_server_params.yaml'),
            description='Absolute path to the map server parameter file'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the simulation clock'),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Activate the map server automatically'),
        map_server,
        lifecycle_manager,
    ])

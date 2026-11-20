from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    map_file = LaunchConfiguration('map')
    default_map = PathJoinSubstitution([
        FindPackageShare('testbed_bringup'), 'maps', 'testbed_world.yaml',
    ])
    params_file = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'), 'config', 'map_server_params.yaml',
    ])

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Path to the occupancy map YAML file'),
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[params_file, {'yaml_filename': ParameterValue(map_file, value_type=str)}],
            output='screen',
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            parameters=[{'use_sim_time': True, 'autostart': True, 'node_names': ['map_server']}],
            output='screen',
        ),
    ])

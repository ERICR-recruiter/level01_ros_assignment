from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    default_map = PathJoinSubstitution([
        FindPackageShare('testbed_bringup'),
        'maps',
        'testbed_world.yaml'
    ])

    default_params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'),
        'config',
        'nav2_params.yaml'
    ])

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {
                'yaml_filename': map_yaml,
                'use_sim_time': use_sim_time,
            }
        ],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server'],
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the Gazebo simulation clock',
        ),
        DeclareLaunchArgument(
            'map',
            default_value=default_map,
            description='Path to the occupancy-map YAML file',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Path to the Nav2 parameters file',
        ),
        map_server,
        lifecycle_manager,
    ])

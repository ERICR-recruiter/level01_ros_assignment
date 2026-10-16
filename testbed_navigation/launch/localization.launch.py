from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    amcl_params_file = LaunchConfiguration('amcl_params_file')

    default_map = PathJoinSubstitution([
        FindPackageShare('testbed_bringup'),
        'maps', 'testbed_world.yaml'
    ])

    default_params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'),
        'config', 'nav2_params.yaml'
    ])

    default_amcl_params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'),
        'config', 'amcl_params.yaml'
    ])

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {'yaml_filename': map_yaml, 'use_sim_time': use_sim_time}
        ],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file, {'use_sim_time': use_sim_time}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('amcl_params_file', default_value=default_amcl_params),
        map_server,
        amcl,
        lifecycle_manager,
    ])

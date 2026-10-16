from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    amcl_params_file = LaunchConfiguration('amcl_params_file')
    rviz_config = LaunchConfiguration('rvizconfig')

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('testbed_bringup'),
                'launch',
                'testbed_full_bringup.launch.py',
            ])
        ),
        launch_arguments={
            'rvizconfig': rviz_config,
        }.items(),
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('testbed_navigation'),
                'launch',
                'localization.launch.py',
            ])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_yaml,
            'params_file': params_file,
            'amcl_params_file': amcl_params_file,
        }.items(),
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('testbed_navigation'),
                'launch',
                'navigation.launch.py',
            ])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
        }.items(),
    )

    default_map = PathJoinSubstitution([
        FindPackageShare('testbed_bringup'),
        'maps',
        'testbed_world.yaml',
    ])

    default_params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'),
        'config',
        'nav2_params.yaml',
    ])

    default_amcl_params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'),
        'config',
        'amcl_params.yaml',
    ])

    default_rviz = PathJoinSubstitution([
        FindPackageShare('testbed_description'),
        'rviz',
        'full_bringup.rviz',
    ])

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('amcl_params_file', default_value=default_amcl_params),
        DeclareLaunchArgument('rvizconfig', default_value=default_rviz),

        # Start simulation first, then localization, then navigation.
        simulation,
        TimerAction(
            period=12.0,
            actions=[
                localization,
                TimerAction(period=10.0, actions=[navigation]),
            ],
        ),
    ])

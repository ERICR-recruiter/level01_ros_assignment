import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_testbed_nav = get_package_share_directory('testbed_navigation')
    pkg_testbed_bringup = get_package_share_directory('testbed_bringup')

    default_map = os.path.join(pkg_testbed_bringup, 'maps', 'testbed_world.yaml')
    default_params = os.path.join(pkg_testbed_nav, 'config', 'nav2_params.yaml')

    map_arg = DeclareLaunchArgument('map', default_value=default_map, description='Path to map file')
    params_arg = DeclareLaunchArgument('params_file', default_value=default_params, description='Path to params')
    sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true', description='Use sim time')

    localization_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_nav, 'launch', 'localization.launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file': LaunchConfiguration('params_file'),
        }.items()
    )

    navigation_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_nav, 'launch', 'navigation.launch.py')
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file': LaunchConfiguration('params_file'),
        }.items()
    )

    return LaunchDescription([
        map_arg,
        params_arg,
        sim_time_arg,
        localization_cmd,
        navigation_cmd,
    ])

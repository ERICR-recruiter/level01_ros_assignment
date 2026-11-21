import os

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('testbed_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('amcl_params_file')


    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value= "true",
        description= "use gazebo sim clock",
        )

    declare_params_file = DeclareLaunchArgument(
        'amcl_params_file',
        default_value=os.path.join(pkg_nav, 'config', 'amcl_params.yaml'),
        description= "full path for the config file for params"
        )

    #reuse map loader so 1 cmd wsill give map + localization
    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, 'launch',  'map_loader.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output= 'screen',
        parameters=[params_file, {"use_sim_time": use_sim_time}])


    lifecycle_manager = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output= 'screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': ['amcl'],
            }])

    return LaunchDescription([
        declare_use_sim_time,
        declare_params_file,
        map_loader,
        amcl,
        lifecycle_manager,
    ])
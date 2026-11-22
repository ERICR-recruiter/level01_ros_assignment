
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    package_dir = get_package_share_directory('testbed_navigation')

    map_loader_file = os.path.join(
        package_dir,
        'launch',
        'map_loader.launch.py'
    )

    amcl_config_file = os.path.join(
        package_dir,
        'config',
        'amcl_params.yaml'
    )

    default_map_file = os.path.join(
        package_dir,
        'maps',
        'testbed_world.yaml'
    )

    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(map_loader_file),
        launch_arguments={
            'map': map_file,
            'use_sim_time': use_sim_time
        }.items()
    )

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_config_file,
            {
                'use_sim_time': use_sim_time
            }
        ]
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': ['amcl']
            }
        ]
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'map',
            default_value=default_map_file,
            description='Full path to the map YAML file'
        ),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),

        map_loader,
        amcl_node,
        lifecycle_manager_node

    ])


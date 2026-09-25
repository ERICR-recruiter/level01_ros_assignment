import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config',
        'nav2_params.yaml'
    )

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            )
        ]),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': params_file,
        }.items()
    )

    return LaunchDescription([
        nav2_bringup_launch
    ])

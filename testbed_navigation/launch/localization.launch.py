import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config',
        'amcl_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')

    use_sim_time_ = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true')

    params_ = DeclareLaunchArgument(
        'params_file',
        default_value=params,
        description='Full path to the AMCL parameters file')

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[LaunchConfiguration('params_file'),
                    {'use_sim_time': use_sim_time}])

    lifecycle_manager_ = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['amcl']}])

    return LaunchDescription([
        use_sim_time_,
        params_,
        amcl,
        lifecycle_manager_,
    ])
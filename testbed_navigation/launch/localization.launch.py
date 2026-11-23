import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Map server is included so localization works standalone
    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_dir, 'launch', 'map_loader.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('params_file', default_value=os.path.join(
            nav_dir, 'config', 'amcl_params.yaml')),
        map_loader,
        Node(package='nav2_amcl', executable='amcl', name='amcl',
             output='screen',
             parameters=[LaunchConfiguration('params_file'),
                         {'use_sim_time': use_sim_time}]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_localization', output='screen',
             parameters=[{'use_sim_time': use_sim_time,
                          'autostart': True,
                          'node_names': ['amcl']}]),
    ])

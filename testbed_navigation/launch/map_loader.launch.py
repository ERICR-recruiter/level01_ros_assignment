import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_testbed_bringup=get_package_share_directory('testbed_bringup')
    map_path=os.path.join(pkg_testbed_bringup,'maps','testbed_world.yaml')

    declare_use_sim_time_cmd= DeclareLaunchArgument(
        'use_sim_time',default_value='True',description="use gz sim time"
    )

    declare_map_path_cmd= DeclareLaunchArgument(
        'map',default_value=map_path,description="map yaml file path"
    )

    start_map_server=Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time':LaunchConfiguration('use_sim_time')},{'yaml_filename': LaunchConfiguration('map')}],
    )
    start_lifecycle_manager=Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')},{'autostart': True},{'node_names':['map_server']}],
    )
    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_map_path_cmd,
        start_map_server,
        start_lifecycle_manager,
    ])
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get the package directory
    nav_pkg_dir = get_package_share_directory('testbed_navigation')
    bringup_pkg_dir = get_package_share_directory('testbed_bringup')

    map_params_file = os.path.join(nav_pkg_dir,'config','map_params.yaml')
    map_yaml_file = os.path.join(bringup_pkg_dir,'maps','testbed_world.yaml')
    
    # Map server node
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            map_params_file,
            {'yaml_filename': map_yaml_file}
        ]
    )
    
    # Lifecycle manager to manage map server
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server']
        }]
    )
    
    return LaunchDescription([
        map_server,
        lifecycle_manager
    ])
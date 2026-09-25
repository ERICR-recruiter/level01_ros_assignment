import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


# This launch file is for publishing the map topic and starting the lifecycle manager for the map server.
# To visualize the map topic , run rviz2 and select 'reliable' and 'transient local' as QOS.
def generate_launch_description():
    pkg_dir = get_package_share_directory('testbed_navigation') # package path 
    map_file = os.path.join(pkg_dir, 'params', 'testbed_world.yaml') # map yaml file 

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    yaml_filename = LaunchConfiguration('map', default=map_file) 

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time},
                    {'yaml_filename': yaml_filename}]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='map_server_lifecycle_manager',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time},
                    {'autostart': True},
                    {'node_names': ['map_server']}]
    )

    return LaunchDescription([
        map_server_node,
        lifecycle_manager
    ])
import os 
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    map_file_arg = DeclareLaunchArgument(
        name='map',
        default_value=os.path.join(
            get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')
        )

    use_sim_time_arg = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
    )

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'yaml_filename': LaunchConfiguration('map'),
            'frame_id': 'map',           # CRITICAL: Explicitly set frame ID
            'topic_name': 'map',          # Explicit topic name
        }],
        remappings=[('map', 'map')]
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': True,                    # automatically activate all nodes below
            'node_names': ['map_server'],         # list of lifecycle nodes to manage
        }]
    )

    return LaunchDescription([
        map_file_arg,
        use_sim_time_arg,
        map_server_node,
        lifecycle_manager_node,
    ])
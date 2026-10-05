import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    package_path = get_package_share_directory('testbed_bringup')

    map_file= os.path.join(package_path,'maps','testbed_world.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')

    use_sim_time_ = DeclareLaunchArgument(
        'use_sim_time', 
        default_value='true'
    )

    map_ = DeclareLaunchArgument(
        'map',
        default_value=map_file,
        description='Full path of map'
    )

    map_server = Node(
                package='nav2_map_server', executable='map_server',
                name='map_server', output='screen',
                parameters=[{'use_sim_time': use_sim_time, 'yaml_filename':LaunchConfiguration('map')}]
            )
    lifecycle_manager_ = Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_map',
                output = 'screen',
                parameters=[{'use_sim_time': use_sim_time,
                             'autostart': True,
                             'node_names': ['map_server']}]
            )

    return LaunchDescription([
        use_sim_time_,
        map_,
        map_server,
        lifecycle_manager_
    ])
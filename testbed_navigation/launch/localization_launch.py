import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('testbed_navigation')
    params_file = os.path.join(pkg_dir, 'params', 'amcl.yaml')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # 1. AMCL Node (Localization)
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('testbed_gazebo'), 'launch', 'spawn_playground.launch.py'),
        )
    )
    gazebo_spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('testbed_gazebo'), 'launch', 'spawn_testbed.launch.py'),
        )
    )
  

    # 2. Lifecycle Manager for AMCL Node
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='amcl_lifecycle_manager',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['amcl']
        }]
    )

    return LaunchDescription([
        amcl_node,
        lifecycle_manager,
        gazebo,
        gazebo_spawn
    ])
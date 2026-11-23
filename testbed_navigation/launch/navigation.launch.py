import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params = LaunchConfiguration('params_file')
    common = dict(output='screen',
                  parameters=[params, {'use_sim_time': use_sim_time}])

    nodes = [
        Node(package='nav2_controller', executable='controller_server',
             name='controller_server', **common),
        Node(package='nav2_planner', executable='planner_server',
             name='planner_server', **common),
        Node(package='nav2_behaviors', executable='behavior_server',
             name='behavior_server', **common),
        Node(package='nav2_bt_navigator', executable='bt_navigator',
             name='bt_navigator', **common),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_navigation', output='screen',
             parameters=[{'use_sim_time': use_sim_time,
                          'autostart': True,
                          'node_names': ['controller_server',
                                         'planner_server',
                                         'behavior_server',
                                         'bt_navigator']}]),
    ]
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('params_file', default_value=os.path.join(
            nav_dir, 'config', 'nav2_params.yaml')),
        *nodes,
    ])

from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'), 'config', 'nav2_params.yaml'
    ])
    return LaunchDescription([
        Node(package='nav2_controller', executable='controller_server',
             name='controller_server', output='screen', parameters=[params]),
        Node(package='nav2_planner', executable='planner_server',
             name='planner_server', output='screen', parameters=[params]),
        Node(package='nav2_behaviors', executable='behavior_server',
             name='behavior_server', output='screen', parameters=[params]),
        Node(package='nav2_bt_navigator', executable='bt_navigator',
             name='bt_navigator', output='screen', parameters=[params]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_navigation', output='screen', parameters=[{
                 'use_sim_time': True, 'autostart': True,
                 'bond_timeout': 30.0,
                 'node_names': ['controller_server', 'planner_server', 'behavior_server', 'bt_navigator'],
             }]),
    ])

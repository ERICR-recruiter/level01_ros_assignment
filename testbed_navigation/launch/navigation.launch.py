from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'), 'config', 'nav2_params.yaml',
    ])
    servers = [
        ('nav2_planner', 'planner_server'),
        ('nav2_controller', 'controller_server'),
        ('nav2_behaviors', 'behavior_server'),
        ('nav2_bt_navigator', 'bt_navigator'),
    ]
    nodes = [
        Node(package=package, executable=name, name=name, parameters=[params_file], output='screen')
        for package, name in servers
    ]
    nodes.append(Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [name for _, name in servers],
        }],
        output='screen',
    ))
    return LaunchDescription(nodes)

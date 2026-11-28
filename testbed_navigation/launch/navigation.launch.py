import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    params_file = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config', 'nav2_params.yaml')

    lifecycle_nodes = ['controller_server', 'planner_server',
                       'behavior_server', 'bt_navigator']

    controller = Node(
        package='nav2_controller', executable='controller_server',
        name='controller_server', output='screen',
        parameters=[params_file])

    planner = Node(
        package='nav2_planner', executable='planner_server',
        name='planner_server', output='screen',
        parameters=[params_file])

    behaviors = Node(
        package='nav2_behaviors', executable='behavior_server',
        name='behavior_server', output='screen',
        parameters=[params_file])

    bt_navigator = Node(
        package='nav2_bt_navigator', executable='bt_navigator',
        name='bt_navigator', output='screen',
        parameters=[params_file])

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_navigation', output='screen',
        parameters=[{'use_sim_time': True,
                     'autostart': True,
                     'node_names': lifecycle_nodes}])

    return LaunchDescription([controller, planner, behaviors,
                              bt_navigator, lifecycle_manager])
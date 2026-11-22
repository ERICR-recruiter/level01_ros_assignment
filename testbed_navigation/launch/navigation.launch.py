import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    nav2_params = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config',
        'nav2_params.yaml')

    # The four Nav2 servers. Node names must match the top-level keys in nav2_params.yaml
    lifecycle_nodes = ['planner_server', 'controller_server',
                       'behavior_server', 'bt_navigator']

    planner = Node(package='nav2_planner', executable='planner_server',
                   name='planner_server', output='screen',
                   parameters=[nav2_params])

    controller = Node(package='nav2_controller', executable='controller_server',
                      name='controller_server', output='screen',
                      parameters=[nav2_params])

    behaviors = Node(package='nav2_behaviors', executable='behavior_server',
                     name='behavior_server', output='screen',
                     parameters=[nav2_params])

    bt_navigator = Node(package='nav2_bt_navigator', executable='bt_navigator',
                        name='bt_navigator', output='screen',
                        parameters=[nav2_params])

    # Brings the four servers up in order: configure, then activate
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': lifecycle_nodes,
        }],
    )

    return LaunchDescription([
        planner,
        controller,
        behaviors,
        bt_navigator,
        lifecycle_manager,
    ])

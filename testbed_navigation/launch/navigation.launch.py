
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    params_file = (
        '/home/payal/assignment_ws/src/level01_ros_assignment/'
        'testbed_navigation/config/nav2_params.yaml'
    )

    # 1. Planner Server: calculates the path to the goal
    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': True}]
    )

    # 2. Controller Server: follows the calculated path
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': True}]
    )

    # 3. Behavior Server: provides recovery behaviors
    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': True}]
    )

    # 4. BT Navigator: coordinates the navigation process
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[params_file, {'use_sim_time': True}]
    )

    # 5. Lifecycle Manager: configures and activates Nav2 nodes
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                'autostart': True,
                'node_names': [
                    'planner_server',
                    'controller_server',
                    'behavior_server',
                    'bt_navigator'
                ]
            }
        ]
    )

    return LaunchDescription([
        planner_server,
        controller_server,
        behavior_server,
        bt_navigator,
        lifecycle_manager
    ])

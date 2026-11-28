import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(get_package_share_directory('testbed_navigation'),
                          'config', 'nav2_params.yaml')

    def nav_node(package, executable, name):
        return Node(package=package, executable=executable, name=name,
                    output='screen', parameters=[params])

    controller = nav_node('nav2_controller', 'controller_server', 'controller_server')
    planner = nav_node('nav2_planner', 'planner_server', 'planner_server')
    behaviors = nav_node('nav2_behaviors', 'behavior_server', 'behavior_server')
    bt_nav = nav_node('nav2_bt_navigator', 'bt_navigator', 'bt_navigator')

    lifecycle = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_navigation', output='screen',
        parameters=[{'use_sim_time': True, 'autostart': True,
                     'node_names': ['controller_server', 'planner_server',
                                    'behavior_server', 'bt_navigator']}])

    return LaunchDescription([controller, planner, behaviors, bt_nav, lifecycle])

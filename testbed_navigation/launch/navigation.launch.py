import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')
    bt_xml = os.path.join(get_package_share_directory('nav2_bt_navigator'),
                          'behavior_trees', 'navigate_to_pose_w_replanning_and_recovery.xml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    common = [params_file, {'use_sim_time': use_sim_time}]

    nodes = ['controller_server', 'planner_server', 'behavior_server', 'bt_navigator']

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use Gazebo /clock'),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(nav_share, 'config', 'nav2_params.yaml'),
                              description='Nav2 parameter file'),

        Node(package='nav2_controller', executable='controller_server', name='controller_server',
             output='screen', parameters=common),
        Node(package='nav2_planner', executable='planner_server', name='planner_server',
             output='screen', parameters=common),
        Node(package='nav2_behaviors', executable='behavior_server', name='behavior_server',
             output='screen', parameters=common),
        Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator',
             output='screen', parameters=common + [{'default_nav_to_pose_bt_xml': bt_xml}]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'autostart': True,
                         'node_names': nodes}],
        ),
    ])

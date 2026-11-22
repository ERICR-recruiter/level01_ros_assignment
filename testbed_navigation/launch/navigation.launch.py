import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

LIFECYCLE_NODES = [
    'controller_server',
    'planner_server',
    'behavior_server',
    'bt_navigator',
    'waypoint_follower',
    'velocity_smoother',
    'collision_monitor',
]


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('nav_params_file')
    bt_xml = LaunchConfiguration('bt_xml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    params = [params_file, {'use_sim_time': use_sim_time}]

    def nav2_node(package, executable, extra_params=None, remappings=None):
        return Node(
            package=package,
            executable=executable,
            name=executable,
            output='screen',
            parameters=params + ([extra_params] if extra_params else []),
            remappings=remappings or [],
        )

    return LaunchDescription([
        DeclareLaunchArgument(
            'nav_params_file',
            default_value=os.path.join(nav_share, 'config', 'nav2_params.yaml')),
        DeclareLaunchArgument(
            'bt_xml',
            default_value=os.path.join(nav_share, 'behavior_trees', 'navigate_to_pose_testbed.xml')),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),

        # cmd_vel goes controller -> velocity_smoother -> collision_monitor -> robot
        nav2_node('nav2_controller', 'controller_server', remappings=[('cmd_vel', 'cmd_vel_nav')]),
        nav2_node('nav2_planner', 'planner_server'),
        nav2_node('nav2_behaviors', 'behavior_server', remappings=[('cmd_vel', 'cmd_vel_nav')]),
        nav2_node('nav2_bt_navigator', 'bt_navigator',
                  extra_params={'default_nav_to_pose_bt_xml': bt_xml}),
        nav2_node('nav2_waypoint_follower', 'waypoint_follower'),
        nav2_node('nav2_velocity_smoother', 'velocity_smoother',
                  remappings=[('cmd_vel', 'cmd_vel_nav')]),
        nav2_node('nav2_collision_monitor', 'collision_monitor'),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'autostart': autostart,
                         'node_names': LIFECYCLE_NODES}],
        ),
    ])

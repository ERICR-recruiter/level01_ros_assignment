import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    sim_time = ParameterValue(use_sim_time, value_type=bool)
    params_file = LaunchConfiguration('params_file')
    bt_xml = LaunchConfiguration('bt_xml')

    # controller output goes through the velocity smoother before the robot
    controller_remaps = [('cmd_vel', 'cmd_vel_nav')]
    smoother_remaps = [('cmd_vel', 'cmd_vel_nav'), ('cmd_vel_smoothed', 'cmd_vel')]

    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'velocity_smoother',
    ]

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'nav2_params.yaml')),
        DeclareLaunchArgument(
            'bt_xml',
            default_value=os.path.join(nav_dir, 'behavior_trees', 'navigate_to_pose.xml')),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': sim_time}],
            remappings=controller_remaps),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': sim_time}]),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': sim_time}]),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[params_file,
                        {'use_sim_time': sim_time,
                         'default_nav_to_pose_bt_xml': bt_xml}]),

        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[params_file, {'use_sim_time': sim_time}],
            remappings=smoother_remaps),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': sim_time,
                         'autostart': True,
                         'node_names': lifecycle_nodes}]),
    ])

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

# Order is important: the lifecycle manager configures/activates in this order.
# slam_toolbox goes first because the costmaps need its map -> odom transform.
lifecycle_nodes = [
    'controller_server',
    'planner_server',
    'behavior_server',
    'bt_navigator',
    'waypoint_follower',
]

ARGUMENTS = [
    DeclareLaunchArgument(
        'use_sim_time', default_value='True', choices=['True', 'False'],
        description='Use simulation time'),
    DeclareLaunchArgument(
        'log_level', default_value='info',
        description='Log level'),   
    DeclareLaunchArgument(
        'cmd_vel_topic', default_value='/robot/diff_drive_controller/cmd_vel',
        description='Topic your robot base listens to for velocity commands'),
]


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    log_level = LaunchConfiguration('log_level')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')

    pkg = get_package_share_directory('testbed_navigation')
    nav_params_file = PathJoinSubstitution([pkg, 'config', 'nav2_params.yaml'])


    # ---------------- Nav2 servers ----------------
    controller_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[nav_params_file, {'use_sim_time': use_sim_time}],
    )

    planner_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[nav_params_file, {'use_sim_time': use_sim_time}],
    )

    behavior_node = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[nav_params_file, {'use_sim_time': use_sim_time}],
        remappings=[('cmd_vel', cmd_vel_topic)],
    )

    bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[nav_params_file, {'use_sim_time': use_sim_time}],
    )

    waypoint_follower_node = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[nav_params_file, {'use_sim_time': use_sim_time}],
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='both',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[{'use_sim_time': use_sim_time},
                    {'autostart': True},
                    {'node_names': lifecycle_nodes}],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(controller_node)
    ld.add_action(planner_node)
    ld.add_action(behavior_node)
    ld.add_action(bt_navigator_node)
    ld.add_action(waypoint_follower_node)
    ld.add_action(lifecycle_manager_node)
    return ld
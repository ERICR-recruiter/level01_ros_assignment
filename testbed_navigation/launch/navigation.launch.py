import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_testbed_nav = get_package_share_directory('testbed_navigation')
    default_params_file = os.path.join(pkg_testbed_nav, 'config', 'nav2_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')

    lifecycle_nodes = [
        'controller_server',
        'smoother_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'waypoint_follower',
        'velocity_smoother'
    ]

    remappings = [
        ('/tf', 'tf'),
        ('/tf_static', 'tf_static')
    ]

    stdout_linebuf_envvar = SetEnvironmentVariable(
        'RCUTILS_LOGGING_BUFFERED_STREAM', '1'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to parameter file for Navigation stack'
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )

    # Controller Server (Local Planner)
    start_controller_server_cmd = Node(
        package='nav2_controller',
        executable='controller_server',
        output='screen',
        emulate_tty=True,
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings + [('cmd_vel', 'cmd_vel_nav')]
    )

    # Smoother Server (Path Smoothing)
    start_smoother_server_cmd = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        emulate_tty=True,
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )

    # Planner Server (Global Planner)
    start_planner_server_cmd = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        emulate_tty=True,
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )

    # Behavior Server (Recoveries: Spin, Backup, Wait, etc.)
    start_behavior_server_cmd = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        emulate_tty=True,
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )

    # BT Navigator (Behavior Tree Navigator for NavigateToPose actions)
    start_bt_navigator_cmd = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        emulate_tty=True,
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )

    # Waypoint Follower
    start_waypoint_follower_cmd = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        emulate_tty=True,
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )

    # Velocity Smoother (Smooths velocity commands before sending to Gazebo base)
    start_velocity_smoother_cmd = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        emulate_tty=True,
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings + [('cmd_vel', 'cmd_vel_nav'), ('cmd_vel_smoothed', 'cmd_vel')]
    )

    # Lifecycle Manager for Navigation action stack
    start_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        emulate_tty=True,
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': autostart},
            {'node_names': lifecycle_nodes}
        ]
    )

    ld = LaunchDescription()

    ld.add_action(stdout_linebuf_envvar)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_autostart_cmd)

    ld.add_action(start_controller_server_cmd)
    ld.add_action(start_smoother_server_cmd)
    ld.add_action(start_planner_server_cmd)
    ld.add_action(start_behavior_server_cmd)
    ld.add_action(start_bt_navigator_cmd)
    ld.add_action(start_waypoint_follower_cmd)
    ld.add_action(start_velocity_smoother_cmd)
    ld.add_action(start_lifecycle_manager_cmd)

    return ld

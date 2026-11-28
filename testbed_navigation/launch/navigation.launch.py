"""
Stage 3: the navigation servers, composed by hand from individual Nav2 nodes.

Starts (all parameters from config/nav2_params.yaml):
  * controller_server   - local costmap + path-following controller plugin
  * planner_server      - global costmap + global planner plugin; serves ComputePathToPose
  * behavior_server     - recovery behaviors (spin, backup, drive_on_heading, wait)
  * bt_navigator        - NavigateToPose / NavigateThroughPoses actions driven by a behavior tree
  * waypoint_follower   - FollowWaypoints action (sequences NavigateToPose goals)
  * velocity_smoother   - limits velocity and acceleration of the commands
  * collision_monitor   - last safety gate before the robot: stops/slows on /scan polygons
  * lifecycle_manager_navigation - configures and activates the seven servers above, in order

Velocity command chain:
  controller_server / behavior_server --cmd_vel_nav--> velocity_smoother
      --cmd_vel_smoothed--> collision_monitor --cmd_vel--> Gazebo diff drive plugin

Requires map_loader.launch.py and localization.launch.py (TF map->odom).

Run:
  ros2 launch testbed_navigation navigation.launch.py
Verify: `ros2 action list` shows /navigate_to_pose; send a goal with the RViz "Nav2 Goal" tool.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterFile
from launch_ros.parameter_descriptions import ParameterValue
from nav2_common.launch import RewrittenYaml


# Startup order: the lifecycle manager configures/activates in this order and shuts down in
# reverse. The servers precede bt_navigator, which needs their action servers.
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

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    declare_args = [
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock instead of wall time'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_share, 'config', 'nav2_params.yaml'),
            description='Absolute path to the Nav2 parameter file'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Configure and activate the navigation servers automatically'),
        DeclareLaunchArgument(
            'log_level', default_value='info',
            description='ROS log level (debug, info, warn, error)'),
    ]

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key='',
            param_rewrites={'use_sim_time': use_sim_time, 'autostart': autostart},
            convert_types=True),
        allow_substs=True)

    # No-op without a namespace; kept so the stack can be namespaced (as in nav2_bringup).
    tf_remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    def nav2_node(package, executable, extra_remappings=()):
        return Node(
            package=package,
            executable=executable,
            name=executable,
            output='screen',
            arguments=['--ros-args', '--log-level', log_level],
            parameters=[configured_params],
            remappings=tf_remappings + list(extra_remappings))

    nodes = [
        # Raw controller output goes to the smoother, never straight to the robot.
        nav2_node('nav2_controller', 'controller_server', [('cmd_vel', 'cmd_vel_nav')]),
        nav2_node('nav2_planner', 'planner_server'),
        # Recovery commands (spin, backup, ...) also go through the smoother and collision monitor.
        nav2_node('nav2_behaviors', 'behavior_server', [('cmd_vel', 'cmd_vel_nav')]),
        nav2_node('nav2_bt_navigator', 'bt_navigator'),
        nav2_node('nav2_waypoint_follower', 'waypoint_follower'),
        # Subscribes cmd_vel (remapped to cmd_vel_nav), publishes cmd_vel_smoothed.
        nav2_node('nav2_velocity_smoother', 'velocity_smoother', [('cmd_vel', 'cmd_vel_nav')]),
        # Input/output topics (cmd_vel_smoothed -> cmd_vel) are set in nav2_params.yaml.
        nav2_node('nav2_collision_monitor', 'collision_monitor'),
    ]

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[{
            'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            'autostart': ParameterValue(autostart, value_type=bool),
            'node_names': LIFECYCLE_NODES,
        }])

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),
        *declare_args,
        *nodes,
        lifecycle_manager,
    ])

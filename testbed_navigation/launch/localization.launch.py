"""
Stage 2: localize the robot on the map with AMCL.

Starts:
  * nav2_amcl/amcl                  - particle filter; subscribes /scan, /map, /initialpose and
                                      TF odom->base_footprint; publishes TF map->odom,
                                      /amcl_pose and /particle_cloud
  * lifecycle_manager_localization  - configures and activates amcl, then bonds to it

The map is not loaded here; start map_loader.launch.py first (or use bringup_all.launch.py).
Keeping the stages separate lets each be started, restarted and debugged on its own.

Run:
  ros2 launch testbed_navigation localization.launch.py
  ros2 launch testbed_navigation localization.launch.py params_file:=/abs/path/amcl.yaml
Verify: the /particle_cloud in RViz2 converges around the robot as it moves, and
  `ros2 run tf2_ros tf2_echo map odom` returns a transform.
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
            default_value=os.path.join(nav_share, 'config', 'amcl_params.yaml'),
            description='Absolute path to the AMCL parameter file'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Configure and activate amcl automatically'),
        DeclareLaunchArgument(
            'log_level', default_value='info',
            description='ROS log level (debug, info, warn, error)'),
    ]

    # The use_sim_time launch argument overrides the value in the YAML file.
    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key='',
            param_rewrites={'use_sim_time': use_sim_time},
            convert_types=True),
        allow_substs=True)

    # No-op without a namespace; kept so the stack can be namespaced (as in nav2_bringup).
    tf_remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[configured_params],
        remappings=tf_remappings)

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[{
            'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            'autostart': ParameterValue(autostart, value_type=bool),
            'node_names': ['amcl'],
        }])

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),
        *declare_args,
        amcl,
        lifecycle_manager,
    ])

"""
Stage 1: load the static map.

Starts:
  * nav2_map_server/map_server  - parameters from config/map_server_params.yaml; reads
                                  testbed_bringup/maps/testbed_world.yaml and publishes
                                  nav_msgs/OccupancyGrid on /map (transient local)
  * lifecycle_manager_map       - configures and activates map_server, then bonds to it

Run (with the simulation, or standalone to inspect the map):
  ros2 launch testbed_navigation map_loader.launch.py
  ros2 launch testbed_navigation map_loader.launch.py map:=/abs/path/other_map.yaml
  ros2 launch testbed_navigation map_loader.launch.py params_file:=/abs/path/map_params.yaml
Verify: RViz2, fixed frame `map`, add a Map display on /map with Durability = Transient Local.
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
    bringup_share = get_package_share_directory('testbed_bringup')
    nav_share = get_package_share_directory('testbed_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    declare_args = [
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock instead of wall time'),
        DeclareLaunchArgument(
            'map', default_value=os.path.join(bringup_share, 'maps', 'testbed_world.yaml'),
            description='Absolute path to the map YAML file'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_share, 'config', 'map_server_params.yaml'),
            description='Absolute path to the map_server parameter file'),
        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Configure and activate map_server automatically'),
        DeclareLaunchArgument(
            'log_level', default_value='info',
            description='ROS log level (debug, info, warn, error)'),
    ]

    sim_time = ParameterValue(use_sim_time, value_type=bool)

    # Launch arguments override the YAML: `map` sets yaml_filename to an absolute path, and
    # `use_sim_time` keeps every node of the stack on the same clock.
    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key='',
            param_rewrites={'use_sim_time': use_sim_time, 'yaml_filename': map_yaml},
            convert_types=True),
        allow_substs=True)

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[configured_params])

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[{
            'use_sim_time': sim_time,
            'autostart': ParameterValue(autostart, value_type=bool),
            'node_names': ['map_server'],
        }])

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),
        *declare_args,
        map_server,
        lifecycle_manager,
    ])

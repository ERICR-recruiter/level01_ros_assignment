#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_testbed_bringup = get_package_share_directory("testbed_bringup")
    pkg_testbed_navigation = get_package_share_directory("testbed_navigation")

    default_map_file = os.path.join(
        pkg_testbed_bringup, "maps", "testbed_world.yaml"
    )
    default_params_file = os.path.join(
        pkg_testbed_navigation, "config", "map_server_params.yaml"
    )

    map_yaml_file = LaunchConfiguration("map")
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")

    declare_map_arg = DeclareLaunchArgument(
        "map",
        default_value=default_map_file,
        description="Full path to the map YAML file to load",
    )
    declare_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock if true",
    )
    declare_autostart_arg = DeclareLaunchArgument(
        "autostart",
        default_value="true",
        description="Automatically configure and activate map_server",
    )

    map_server_node = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            default_params_file,
            {
                "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                "yaml_filename": map_yaml_file,
            },
        ],
    )

    lifecycle_manager_map = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_map",
        output="screen",
        parameters=[
            {
                "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                "autostart": ParameterValue(autostart, value_type=bool),
                "node_names": ["map_server"],
            }
        ],
    )

    return LaunchDescription([
        declare_map_arg,
        declare_sim_time_arg,
        declare_autostart_arg,
        map_server_node,
        lifecycle_manager_map,
    ])

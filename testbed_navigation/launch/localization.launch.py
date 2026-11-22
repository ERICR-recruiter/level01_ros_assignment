#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_testbed_navigation = get_package_share_directory("testbed_navigation")

    default_amcl_params = os.path.join(
        pkg_testbed_navigation, "config", "amcl_params.yaml"
    )

    amcl_params_file = LaunchConfiguration("params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")

    declare_params_arg = DeclareLaunchArgument(
        "params_file",
        default_value=default_amcl_params,
        description="Full path to the AMCL parameters YAML file",
    )
    declare_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock if true",
    )
    declare_autostart_arg = DeclareLaunchArgument(
        "autostart",
        default_value="true",
        description="Automatically configure and activate AMCL",
    )

    configured_params = RewrittenYaml(
        source_file=amcl_params_file,
        param_rewrites={"use_sim_time": use_sim_time},
        convert_types=True,
    )

    amcl_node = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[configured_params],
    )

    # Dedicated lifecycle manager so localization can be launched independently
    # alongside map_loader.launch.py without node-name conflicts.
    lifecycle_manager_localization = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {
                "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                "autostart": ParameterValue(autostart, value_type=bool),
                "node_names": ["amcl"],
            }
        ],
    )

    return LaunchDescription([
        declare_params_arg,
        declare_sim_time_arg,
        declare_autostart_arg,
        amcl_node,
        lifecycle_manager_localization,
    ])

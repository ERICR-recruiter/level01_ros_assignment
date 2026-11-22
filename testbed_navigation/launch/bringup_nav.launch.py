#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_testbed_navigation = get_package_share_directory("testbed_navigation")
    pkg_testbed_bringup = get_package_share_directory("testbed_bringup")

    default_map_file = os.path.join(
        pkg_testbed_bringup, "maps", "testbed_world.yaml"
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_yaml_file = LaunchConfiguration("map")

    declare_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock if true",
    )
    declare_map_arg = DeclareLaunchArgument(
        "map",
        default_value=default_map_file,
        description="Full path to the map YAML file",
    )

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_navigation, "launch", "map_loader.launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "map": map_yaml_file,
        }.items(),
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_navigation, "launch", "localization.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_testbed_navigation, "launch", "navigation.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    return LaunchDescription([
        declare_sim_time_arg,
        declare_map_arg,
        map_loader,
        localization,
        navigation,
    ])

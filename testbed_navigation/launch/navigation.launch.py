#!/usr/bin/env python3
"""Manual Nav2 bringup for Testbed-T1.0.0 (ROS 2 Humble).

Start Gazebo separately with testbed_full_bringup.launch.py.
This launch file includes the existing map + AMCL localization launch,
then starts the Nav2 planner, controller, behavior and BT navigator servers.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = get_package_share_directory("testbed_navigation")
    nav2_params = os.path.join(package_dir, "config", "nav2_params.yaml")
    localization_launch = os.path.join(
        package_dir, "launch", "localization.launch.py"
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_file = LaunchConfiguration("map")

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(localization_launch),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "map": map_file,
        }.items(),
    )

    common_params = [nav2_params, {"use_sim_time": use_sim_time}]

    planner_server = Node(
        package="nav2_planner",
        executable="planner_server",
        name="planner_server",
        output="screen",
        parameters=common_params,
    )

    controller_server = Node(
        package="nav2_controller",
        executable="controller_server",
        name="controller_server",
        output="screen",
        parameters=common_params,
        remappings=[("cmd_vel", "/cmd_vel")],
    )

    behavior_server = Node(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        output="screen",
        parameters=common_params,
    )

    bt_navigator = Node(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        output="screen",
        parameters=common_params,
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "autostart": True,
            "node_names": [
                "planner_server",
                "controller_server",
                "behavior_server",
                "bt_navigator",
            ],
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use Gazebo simulation clock",
        ),
        DeclareLaunchArgument(
            "map",
            default_value=os.path.join(
                package_dir, "maps", "testbed_world.yaml"
            ),
            description="Map YAML file",
        ),
        localization,
        planner_server,
        controller_server,
        behavior_server,
        bt_navigator,
        lifecycle_manager,
    ])


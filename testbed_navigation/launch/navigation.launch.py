#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    params_file = (
        "/home/harsh/assignment_ws/"
        "src/level01_ros_assignment/"
        "testbed_navigation/config/nav2_params.yaml"
    )

    planner_server = Node(
        package="nav2_planner",
        executable="planner_server",
        name="planner_server",
        output="screen",
        parameters=[params_file],
    )

    controller_server = Node(
        package="nav2_controller",
        executable="controller_server",
        name="controller_server",
        output="screen",
        parameters=[params_file],
    )

    bt_navigator = Node(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        output="screen",
        parameters=[params_file],
    )

    behavior_server = Node(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        output="screen",
        parameters=[params_file],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="navigation_lifecycle_manager",
        output="screen",
        parameters=[
            {
                "use_sim_time": True,
                "autostart": True,
                "node_names": [
                    "planner_server",
                    "controller_server",
                    "bt_navigator",
                    "behavior_server",
                ],
            }
        ],
    )

    return LaunchDescription(
        [
            planner_server,
            controller_server,
            bt_navigator,
            behavior_server,
            lifecycle_manager,
        ]
    )
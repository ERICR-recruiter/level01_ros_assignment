import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    navigation_share = get_package_share_directory("testbed_navigation")
    bt_share = get_package_share_directory("nav2_bt_navigator")

    params_file = os.path.join(navigation_share, "config", "nav2_params.yaml")
    bt_file = os.path.join(
        bt_share,
        "behavior_trees",
        "navigate_to_pose_w_replanning_and_recovery.xml",
    )

    planner_server = Node(
        package="nav2_planner",
        executable="planner_server",
        name="planner_server",
        output="screen",
        parameters=[
            params_file,
            {"use_sim_time": True},
        ],
    )

    controller_server = Node(
        package="nav2_controller",
        executable="controller_server",
        name="controller_server",
        output="screen",
        parameters=[
            params_file,
            {"use_sim_time": True},
        ],
        remappings=[
            ("cmd_vel", "/cmd_vel"),
        ],
    )

    behavior_server = Node(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        output="screen",
        parameters=[
            params_file,
            {"use_sim_time": True},
        ],
        remappings=[
            ("cmd_vel", "/cmd_vel"),
        ],
    )

    bt_navigator = Node(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        output="screen",
        parameters=[
            params_file,
            {
                "use_sim_time": True,
                "default_nav_to_pose_bt_xml": bt_file,
            },
        ],
    )

    waypoint_follower = Node(
        package="nav2_waypoint_follower",
        executable="waypoint_follower",
        name="waypoint_follower",
        output="screen",
        parameters=[
            params_file,
            {"use_sim_time": True},
        ],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="navigation_lifecycle_manager",
        output="screen",
        parameters=[
            {"use_sim_time": True},
            {"autostart": True},
            {
                "node_names": [
                    "planner_server",
                    "controller_server",
                    "behavior_server",
                    "bt_navigator",
                    "waypoint_follower",
                ],
            },
        ],
    )

    return LaunchDescription([
        planner_server,
        controller_server,
        behavior_server,
        bt_navigator,
        waypoint_follower,
        lifecycle_manager,
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    map_default = os.path.join(
        get_package_share_directory("testbed_bringup"),
        "maps",
        "testbed_world.yaml",
    )
    map_yaml = LaunchConfiguration("map")
    use_sim_time = LaunchConfiguration("use_sim_time")

    return LaunchDescription([
        DeclareLaunchArgument("map", default_value=map_default),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            output="screen",
            parameters=[
                os.path.join(
                    get_package_share_directory("testbed_navigation"),
                    "config",
                    "map_server.yaml",
                ),
                {"yaml_filename": map_yaml, "use_sim_time": use_sim_time},
            ],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_map",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": ["map_server"],
            }],
        ),
    ])

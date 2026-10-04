import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    navigation_share = get_package_share_directory("testbed_navigation")
    bringup_share = get_package_share_directory("testbed_bringup")

    amcl_params = os.path.join(navigation_share, "config", "amcl_params.yaml")
    map_file = os.path.join(bringup_share, "maps", "testbed_world.yaml")

    map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            {"yaml_filename": map_file},
            {"use_sim_time": True},
        ],
    )

    amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[
            amcl_params,
            {"use_sim_time": True},
        ],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="localization_lifecycle_manager",
        output="screen",
        parameters=[
            {"use_sim_time": True},
            {"autostart": True},
            {"node_names": ["map_server", "amcl"]},
        ],
    )

    return LaunchDescription([map_server, amcl, lifecycle_manager])

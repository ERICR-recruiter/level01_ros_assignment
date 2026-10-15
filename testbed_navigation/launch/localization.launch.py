
import os
from launch.actions import DeclareLaunchArgument, TimerAction
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")

    params_file = os.path.join(
        get_package_share_directory("testbed_navigation"),
        "config",
        "amcl_params.yaml",
    )

    amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[
            params_file,
            {"use_sim_time": use_sim_time},
        ],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "autostart": True, "bond_timeout": 0.0,
                "node_names": ["amcl"],
            }
        ],
    )

    return LaunchDescription(
        [
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        amcl,
        TimerAction(period=2.0, actions=[lifecycle_manager]),
    ]
    )

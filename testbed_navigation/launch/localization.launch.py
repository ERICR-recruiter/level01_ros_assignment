from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node
import os

PKG_NAME = "testbed_navigation"


def generate_launch_description():

    params_file  = LaunchConfiguration("params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart    = LaunchConfiguration("autostart")

    declare_params = DeclareLaunchArgument(
        "params_file",
        default_value=os.path.join(
            get_package_share_directory(PKG_NAME), "config", "amcl_params.yaml"
        ),
    )

    declare_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
    )

    declare_autostart = DeclareLaunchArgument(
        "autostart",
        default_value="true",
    )

    amcl_node = LifecycleNode(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        namespace="",
        output="screen",
        parameters=[params_file, {"use_sim_time": use_sim_time}],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "autostart": autostart,
            "node_names": ["amcl"],
        }],
    )

    return LaunchDescription([
        declare_params,
        declare_sim_time,
        declare_autostart,
        amcl_node,
        lifecycle_manager,
    ])
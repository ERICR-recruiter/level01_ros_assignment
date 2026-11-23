import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    ## Launch configurations
    use_sim_time = LaunchConfiguration("use_sim_time")
    amcl_config = LaunchConfiguration("amcl_config")
    map_yaml = LaunchConfiguration("map_yaml")

    ## lifecycle nodes
    lifecycle_nodes = ["map_server","amcl"]

    ## package directory 

    bringup_dir = get_package_share_directory("testbed_bringup")

    localization_dir = get_package_share_directory(
        "testbed_localization"
    )

    ## Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true"
    )

    amcl_config_arg = DeclareLaunchArgument(
        "amcl_config",
        default_value=os.path.join(
            localization_dir,
            "config",
            "amcl_params.yaml"
        ),
        description="Full path to AMCL paramter file"
    )

    map_yaml_arg = DeclareLaunchArgument(
        "map_yaml",
        default_value=os.path.join(
            bringup_dir,
            "maps",
            "testbed_world.yaml"
        ),
        description="Absolute path to the map YAML file"
    )

    nav2_map_server = Node(
        package = "nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            {"yaml_filename": map_yaml},
            {"use_sim_time": use_sim_time}
        ],
    )

    ## AMCL Node
    nav2_amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        emulate_tty= True,
        parameters=[
            amcl_config,
            {
                "use_sim_time": use_sim_time
            }
        ]
    )


    ## AMCL Lifecycle Manager
    nav2_lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {
                "node_names": lifecycle_nodes,
                "use_sim_time": use_sim_time,
                "autostart": True
            }
        ]
    )


    return LaunchDescription([
        map_yaml_arg,
        use_sim_time_arg,
        amcl_config_arg,
        nav2_map_server,
        nav2_amcl,
        nav2_lifecycle_manager,
    ])
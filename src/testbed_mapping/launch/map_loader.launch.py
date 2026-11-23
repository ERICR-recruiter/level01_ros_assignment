import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Launch configurations
    use_sim_time = LaunchConfiguration("use_sim_time")

    map_file = LaunchConfiguration("map_file")

    # Package directories 
    mapping_dir = get_package_share_directory(
        "testbed_mapping"
    )

    bringup_dir = get_package_share_directory(
        "testbed_bringup"
    )

    ## Paramter file
    map_server_params = os.path.join(
        mapping_dir,
        "config",
        "map_server_params.yaml"
    )

    ## Default map path
    default_map_file = PathJoinSubstitution([
        bringup_dir,
        "maps",
        "testbed_world.yaml"
    ])

    ## Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true"
    )

    map_file_arg = DeclareLaunchArgument(
        "map_file",
        default_value=default_map_file,
        description="Full path to map YAML file"
    )

    ## Map Server
    map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            map_server_params,
            {
                "yaml_filename" : map_file,
                "use_sim_time" : use_sim_time
            }
        ]
    )

    ## Lifecycle manager
    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_map",
        output="screen",
        parameters=[
            {
                "node_names":["map_server"],
                "use_sim_time": use_sim_time,
                "autostart": True
            }
        ]
    )


    return LaunchDescription([
        use_sim_time_arg,
        map_file_arg,
        map_server,
        lifecycle_manager
    ])
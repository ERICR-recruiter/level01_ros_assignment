
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    map_file = LaunchConfiguration("map")
    use_sim_time = LaunchConfiguration("use_sim_time")

    default_map = PathJoinSubstitution([
        FindPackageShare("testbed_bringup"),
        "maps",
        "testbed_world.yaml",
    ])

    return LaunchDescription([

        DeclareLaunchArgument(
            "map",
            default_value=default_map,
            description="Path to the occupancy-grid map YAML file",
        ),

        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use Gazebo simulation time",
        ),

        # Nav2 map server
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            output="screen",
            parameters=[{
                "yaml_filename": map_file,
                "use_sim_time": use_sim_time,
            }],
        ),

        # Activate the lifecycle map server
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

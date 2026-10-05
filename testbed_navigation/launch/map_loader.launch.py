import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")
    params_file = LaunchConfiguration("params_file")

    # static map used by the map server
    map_file = os.path.join(
        get_package_share_directory('testbed_bringup'),
        'maps',
        'testbed_world.yaml'
    )
    default_params_file = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config',
        'map_server_params.yaml'
    )

    # publish the state occupancy grid map from the map YAML file
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {
                "use_sim_time": use_sim_time,
                "yaml_filename": map_file,
            }
        ]
    )

    # manage the lifecycle of the map server automatically
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": ["map_server"],
            }
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation time from the /clock topic.",
        ),
        DeclareLaunchArgument(
            "params_file",
            default_value=default_params_file,
            description="Path to the map server parameter file.",
        ),
        map_server,
        lifecycle_manager
    ])
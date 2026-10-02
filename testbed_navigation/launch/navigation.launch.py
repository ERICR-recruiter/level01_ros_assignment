import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")
    testbed_navigation_pkg = get_package_share_directory("testbed_navigation")

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true"
    )

    nav2_controller_server = Node(
        package="nav2_controller",
        executable="controller_server",
        parameters=[
            os.path.join(testbed_navigation_pkg, "config", "controller_server.yaml"),
            os.path.join(testbed_navigation_pkg, "config", "local_costmap.yaml"),
            {"use_sim_time": use_sim_time}
        ],
        output="screen",
    )

    nav2_planner_server = Node(
        package="nav2_planner",
        executable="planner_server",
        parameters=[
            os.path.join(testbed_navigation_pkg, "config", "planner_server.yaml"),
            os.path.join(testbed_navigation_pkg, "config", "global_costmap.yaml"),
            {"use_sim_time": use_sim_time}
        ],
        output="screen",
    )

    nav2_smoother_server = Node(
        package="nav2_smoother",
        executable="smoother_server",
        name="smoother_server",
        parameters=[
            os.path.join(testbed_navigation_pkg, "config", "smoother_server.yaml"),
            {"use_sim_time": use_sim_time}
        ],
        output="screen",
    )

    nav2_bt_navigator = Node(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        parameters=[
            os.path.join(testbed_navigation_pkg, "config", "bt_navigator.yaml"),
            {"use_sim_time": use_sim_time}
        ],
        output="screen",
    )
    
    nav2_behavior_server = Node(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        parameters=[
            os.path.join(testbed_navigation_pkg, "config", "behavior_server.yaml"),
            {"use_sim_time": use_sim_time}
        ],
        output="screen",
    )

    lifecycle_nodes = [
        "controller_server",
        "planner_server",
        "smoother_server",
        "behavior_server",
        "bt_navigator",
    ]

    nav2_lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[
            {"node_names": lifecycle_nodes},
            {"autostart": True},
            {"use_sim_time": use_sim_time}
        ],
    )
    
    

    return LaunchDescription([
        use_sim_time_arg,
        nav2_controller_server,
        nav2_planner_server,
        nav2_smoother_server,
        nav2_bt_navigator,
        nav2_behavior_server,
        nav2_lifecycle_manager        
    ])
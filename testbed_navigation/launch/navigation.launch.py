import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node, SetParameter

PKG_NAME = "testbed_navigation"


def pkg(path: str) -> str:
    return os.path.join(get_package_share_directory(PKG_NAME), path)


def generate_launch_description() -> LaunchDescription:

    declare_params = DeclareLaunchArgument(
        "params_file",
        default_value=pkg("config/nav2_params.yaml"),
        description="Path to the Nav2 parameter file",
    )
    declare_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use Gazebo simulation clock",
    )
    declare_autostart = DeclareLaunchArgument(
        "autostart",
        default_value="true",
        description="Auto-activate all lifecycle nodes on launch",
    )

    params_file  = LaunchConfiguration("params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart    = LaunchConfiguration("autostart")

    nav2_params = [params_file, {"use_sim_time": use_sim_time}]

    planner_server = LifecycleNode(
        package="nav2_planner",
        executable="planner_server",
        name="planner_server",
        namespace="",
        output="screen",
        parameters=nav2_params,
    )

    controller_server = LifecycleNode(
        package="nav2_controller",
        executable="controller_server",
        name="controller_server",
        namespace="",
        output="screen",
        parameters=nav2_params,
        remappings=[("cmd_vel", "cmd_vel_nav")],
    )

    smoother_server = LifecycleNode(
        package="nav2_smoother",
        executable="smoother_server",
        name="smoother_server",
        namespace="",
        output="screen",
        parameters=nav2_params,
    )

    behavior_server = LifecycleNode(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        namespace="",
        output="screen",
        parameters=nav2_params,
    )

    bt_navigator = LifecycleNode(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        namespace="",
        output="screen",
        parameters=nav2_params,
    )

    waypoint_follower = LifecycleNode(
        package="nav2_waypoint_follower",
        executable="waypoint_follower",
        name="waypoint_follower",
        namespace="",
        output="screen",
        parameters=nav2_params,
    )

    velocity_smoother = Node(
        package="nav2_velocity_smoother",
        executable="velocity_smoother",
        name="velocity_smoother",
        output="screen",
        parameters=nav2_params,
        remappings=[
            ("cmd_vel",     "cmd_vel_nav"),      
            ("cmd_vel_smoothed", "cmd_vel_smoothed"),  
        ],
    )

    collision_monitor = Node(
        package="nav2_collision_monitor",
        executable="collision_monitor",
        name="collision_monitor",
        output="screen",
        parameters=nav2_params,
        remappings=[
            ("cmd_vel",     "cmd_vel_smoothed"),  
            ("cmd_vel_out", "cmd_vel"),         
        ],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "autostart":    autostart,
            "node_names": [
                "planner_server",
                "controller_server",
                "smoother_server",
                "behavior_server",
                "bt_navigator",
                "waypoint_follower",
            ],
        }],
    )

    return LaunchDescription([
        declare_params,
        declare_sim_time,
        declare_autostart,
        LogInfo(msg="[navigation.launch.py] Starting Nav2 stack..."),
        LogInfo(msg="[navigation.launch.py] Ensure map_server and AMCL are already running."),
        planner_server,
        controller_server,
        smoother_server,
        behavior_server,
        bt_navigator,
        waypoint_follower,
        velocity_smoother,
        collision_monitor,
        lifecycle_manager,
    ])
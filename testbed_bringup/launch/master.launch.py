import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, ExecuteProcess, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    bringup_dir = get_package_share_directory('testbed_bringup')
    nav_dir = get_package_share_directory('testbed_navigation')

    #error monitor
    debug_console = ExecuteProcess(
        cmd=['ros2', 'run', 'rqt_console', 'rqt_console'],
        output='screen'
    )

    # 1. Launch the Simulation
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(bringup_dir, 'launch', 'testbed_full_bringup.launch.py'))
    )

    #rviz

    rviz_config_dir = os.path.join(
    get_package_share_directory('testbed_navigation'),
    'rviz',
    'nav.rviz'
    )

    rviz_launch = ExecuteProcess(
    cmd=['ros2', 'run', 'rviz2', 'rviz2', '-d', rviz_config_dir],
    output='screen'
    )

    # 2. Listen for the first LiDAR ping
    wait_for_sim = ExecuteProcess(
        cmd=['ros2', 'topic', 'echo', '--once', '/scan'],
        output='log'
    )

    # 3. Define the Navigation Stack Launches
    map_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav_dir, 'launch', 'map_loader.launch.py'))
    )
    loc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav_dir, 'launch', 'localization.launch.py'))
    )
    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav_dir, 'launch', 'navigation.launch.py'))
    )

    # 4. The Trigger: Once the LiDAR ping is heard, launch Nav2 (with tiny buffers for network settling)
    start_nav_stack = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=wait_for_sim,
            on_exit=[
                map_launch,
                TimerAction(period=2.0, actions=[loc_launch]),
                TimerAction(period=4.0, actions=[nav_launch]),
                TimerAction(period=6.0, actions=[rviz_launch])
            ]
        )
    )

    return LaunchDescription([
        sim_launch,
        debug_console,
        wait_for_sim,
        start_nav_stack
    ])

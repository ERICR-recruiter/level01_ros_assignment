from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config_dir = Path(get_package_share_directory('testbed_navigation')) / 'config'
    params = str(config_dir / 'nav2_params.yaml')

    planner = Node(
        package='nav2_planner', executable='planner_server',
        name='planner_server', output='screen', parameters=[params],
    )
    controller = Node(
        package='nav2_controller', executable='controller_server',
        name='controller_server', output='screen', parameters=[params],
    )
    navigator = Node(
        package='nav2_bt_navigator', executable='bt_navigator',
        name='bt_navigator', output='screen',
        parameters=[params, {
            'default_nav_to_pose_bt_xml': str(config_dir / 'navigate_to_pose.xml'),
            'default_nav_through_poses_bt_xml': str(config_dir / 'navigate_through_poses.xml'),
        }],
    )
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_navigation', output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['planner_server', 'controller_server', 'bt_navigator'],
        }],
    )
    return LaunchDescription([planner, controller, navigator, lifecycle_manager])

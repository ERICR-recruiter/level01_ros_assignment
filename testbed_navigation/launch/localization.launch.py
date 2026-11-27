"""Step 2 - localize the robot on the map with AMCL.

Needs the map from map_loader.launch.py and the simulation (for /scan and the
odom -> base_footprint TF). AMCL then publishes map -> odom.

The initial pose is set in config/amcl_params.yaml to the gazebo spawn point, so the
particle cloud should already be on the robot. If not, use "2D Pose Estimate" in rviz.

    ros2 launch testbed_navigation localization.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_dir = get_package_share_directory('testbed_navigation')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')

    declare_args = [
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'amcl_params.yaml'),
            description='AMCL parameter file'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
    ]

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
    )

    # separate lifecycle manager from the map one, so localization can be
    # restarted without touching the map server
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': autostart,
                     'node_names': ['amcl']}],
    )

    return LaunchDescription(declare_args + [amcl, lifecycle_manager])

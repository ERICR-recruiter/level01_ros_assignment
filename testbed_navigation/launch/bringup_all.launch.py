"""
One-command demo: simulation + map + localization + navigation + RViz.

Composes the three stage launch files of this package; nav2_bringup is not used.

Starts:
  * (launch_sim:=true) Gazebo Classic with testbed_playground.world, robot_state_publisher,
    the Testbed-T1.0.0 spawned at (0, 5, yaw 0), and the odometry EKF (robot_localization).
    testbed_full_bringup is not included, since it would start a second RViz with an
    odom-frame config.
  * map_loader.launch.py    - map_server + lifecycle_manager_map            (immediately)
  * localization.launch.py  - amcl + lifecycle_manager_localization         (after a delay)
  * navigation.launch.py    - Nav2 servers + lifecycle_manager_navigation   (after a delay)
  * (rviz:=true) RViz2 with rviz/nav2.rviz

Run:
  ros2 launch testbed_navigation bringup_all.launch.py
  ros2 launch testbed_navigation bringup_all.launch.py launch_sim:=false   # sim already up
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, TimerAction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

# Seconds before AMCL and Nav2 start. Gazebo needs a few seconds to load the world, spawn the
# robot and start publishing /clock, /scan and odom TF; lifecycle nodes started earlier only
# emit TF/clock warnings, and costmap activation blocks on transforms that do not exist yet.
STACK_START_DELAY = 5.0


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')
    bringup_share = get_package_share_directory('testbed_bringup')
    gazebo_share = get_package_share_directory('testbed_gazebo')
    description_share = get_package_share_directory('testbed_description')
    nav_launch_dir = os.path.join(nav_share, 'launch')

    use_sim_time = LaunchConfiguration('use_sim_time')
    launch_sim = LaunchConfiguration('launch_sim')
    rviz = LaunchConfiguration('rviz')
    rviz_config = LaunchConfiguration('rviz_config')
    map_yaml = LaunchConfiguration('map')
    map_params = LaunchConfiguration('map_params')
    amcl_params = LaunchConfiguration('amcl_params')
    nav2_params = LaunchConfiguration('nav2_params')

    declare_args = [
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo /clock instead of wall time'),
        DeclareLaunchArgument(
            'launch_sim', default_value='true',
            description='Start Gazebo, robot_state_publisher and spawn the robot'),
        DeclareLaunchArgument(
            'rviz', default_value='true',
            description='Start RViz2 with the Nav2 view'),
        DeclareLaunchArgument(
            'rviz_config', default_value=os.path.join(nav_share, 'rviz', 'nav2.rviz'),
            description='Absolute path to the RViz2 config'),
        DeclareLaunchArgument(
            'map', default_value=os.path.join(bringup_share, 'maps', 'testbed_world.yaml'),
            description='Absolute path to the map YAML file'),
        DeclareLaunchArgument(
            'map_params',
            default_value=os.path.join(nav_share, 'config', 'map_server_params.yaml'),
            description='Absolute path to the map_server parameter file'),
        DeclareLaunchArgument(
            'amcl_params', default_value=os.path.join(nav_share, 'config', 'amcl_params.yaml'),
            description='Absolute path to the AMCL parameter file'),
        DeclareLaunchArgument(
            'nav2_params', default_value=os.path.join(nav_share, 'config', 'nav2_params.yaml'),
            description='Absolute path to the Nav2 parameter file'),
    ]

    def include(path, launch_arguments=None):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(path),
            launch_arguments=(launch_arguments or {}).items())

    simulation = GroupAction(
        condition=IfCondition(launch_sim),
        actions=[
            include(os.path.join(gazebo_share, 'launch', 'spawn_playground.launch.py')),
            include(os.path.join(description_share, 'launch', 'robot_description.launch.py'),
                    {'use_sim_time': use_sim_time}),
            include(os.path.join(gazebo_share, 'launch', 'spawn_testbed.launch.py')),
            # Odometry EKF (wheel odometry + IMU), as in testbed_full_bringup.launch.py.
            Node(
                package='robot_localization',
                executable='ekf_node',
                name='ekf_filter_node',
                output='screen',
                parameters=[os.path.join(bringup_share, 'config', 'ekf.yaml'),
                            {'use_sim_time': ParameterValue(use_sim_time, value_type=bool)}]),
        ])

    map_loader = include(
        os.path.join(nav_launch_dir, 'map_loader.launch.py'),
        {'use_sim_time': use_sim_time, 'map': map_yaml, 'params_file': map_params})

    localization = include(
        os.path.join(nav_launch_dir, 'localization.launch.py'),
        {'use_sim_time': use_sim_time, 'params_file': amcl_params})

    navigation = include(
        os.path.join(nav_launch_dir, 'navigation.launch.py'),
        {'use_sim_time': use_sim_time, 'params_file': nav2_params})

    rviz_node = Node(
        condition=IfCondition(rviz),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': ParameterValue(use_sim_time, value_type=bool)}])

    # Each stage is wrapped in a GroupAction to scope its launch configurations: in Humble,
    # IncludeLaunchDescription does not, and all three stages declare 'params_file', so one
    # stage's value would leak into the next.
    return LaunchDescription([
        *declare_args,
        simulation,
        GroupAction([map_loader]),
        rviz_node,
        TimerAction(
            period=STACK_START_DELAY,
            actions=[GroupAction([localization]), GroupAction([navigation])]),
    ])

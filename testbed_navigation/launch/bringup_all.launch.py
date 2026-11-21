import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('testbed_navigation')
    pkg_gazebo = get_package_share_directory('testbed_gazebo')
    pkg_description = get_package_share_directory('testbed_description')

    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz_config = LaunchConfiguration('rviz_config')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use the Gazebo simulation clock')

    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=os.path.join(pkg_nav, 'rviz', 'navigation.rviz'),
        description='Full path to the RViz config file')

    # Env- robot, world, robot spawn
    state_pub = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_description, 'launch', 'robot_description.launch.py')))

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'spawn_playground.launch.py')))

    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'spawn_testbed.launch.py')))

    # Localization - (map server + AMCL)
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, 'launch', 'localization.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    # Navigation - (planner, controller, behaviors, BT navigator)
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, 'launch', 'navigation.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    # RViz configs
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_navigation',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen')

    return LaunchDescription([
        declare_use_sim_time,
        declare_rviz_config,
        state_pub,
        gazebo,
        spawn,
        TimerAction(period=10.0, actions=[localization]),
        TimerAction(period=17.0, actions=[navigation]),
        TimerAction(period=20.0, actions=[rviz]),
    ])

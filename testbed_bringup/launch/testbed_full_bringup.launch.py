#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription,
                            RegisterEventHandler, TimerAction)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

  pkg_testbed_gazebo = get_package_share_directory('testbed_gazebo')
  pkg_testbed_description = get_package_share_directory('testbed_description')

  gazebo = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_testbed_gazebo, 'launch', 'spawn_playground.launch.py'),
    )
  )

  state_pub = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_testbed_description, 'launch', 'robot_description.launch.py'),
    )
  )

  spawn = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_testbed_gazebo, 'launch', 'spawn_testbed.launch.py'),
    )
  )
#the gazebo was crashing again and again and gazebo should publish clock when the world is loaded fully to avoid the crash
  wait_for_world = ExecuteProcess(
    cmd=['ros2', 'topic', 'echo', '--once', '/clock', 'rosgraph_msgs/msg/Clock'],
    output='log',
  )

  spawn_when_world_ready = RegisterEventHandler(
    OnProcessExit(
      target_action=wait_for_world,
      on_exit=[TimerAction(period=LaunchConfiguration('spawn_delay'), actions=[spawn])],
    )
  )

  rviz_config_dir = os.path.join(pkg_testbed_description, 'rviz', 'full_bringup.rviz')

  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz_node',
    parameters=[{'use_sim_time': True}],
    arguments=['-d', LaunchConfiguration('rvizconfig')]
  )

  return LaunchDescription([
    DeclareLaunchArgument(name='rvizconfig', default_value=rviz_config_dir,
                          description='Absolute path to rviz config file'),
    DeclareLaunchArgument(name='spawn_delay', default_value='2.0',
                          description='Extra seconds to wait after the world is running before spawning'),
    gazebo,
    state_pub,
    wait_for_world,
    spawn_when_world_ready,
    rviz_node,
  ])

#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
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
      os.path.join(pkg_testbed_description, 'launch', 'testbed_rviz_barebones.launch.py'),
    )
  )

  spawn = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_testbed_gazebo, 'launch', 'spawn_testbed.launch.py'),
    )
  )

  # Default RViz config path changed to Nav2 default view
  nav2_rviz_config_dir = '/opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz'

  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz_node',
    parameters=[{'use_sim_time': True}],
    arguments=['-d', LaunchConfiguration('rvizconfig')]
  )

  return LaunchDescription([
    DeclareLaunchArgument(
      name='rvizconfig',
      default_value=nav2_rviz_config_dir,
      description='Absolute path to rviz config file'
    ),
    state_pub,
    gazebo,
    spawn,
    rviz_node,
  ])
#!/usr/bin/python3
import os
import launch, launch_ros
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_prefix
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
  
  rviz_config_dir = os.path.join(
    launch_ros.substitutions.FindPackageShare(package='testbed_description').find('testbed_description'),
    'rviz/full_bringup.rviz')
  
  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz_node',
    parameters=[{'use_sim_time': True}],
    arguments=['-d', LaunchConfiguration('rvizconfig')],
    condition=IfCondition(LaunchConfiguration('use_rviz'))
  )

  return LaunchDescription([
    launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=rviz_config_dir,
                                            description='Absolute path to rviz config file'),
    launch.actions.DeclareLaunchArgument(name='use_rviz', default_value='true'),
    state_pub,
    gazebo,
    spawn,
    rviz_node,
  ])
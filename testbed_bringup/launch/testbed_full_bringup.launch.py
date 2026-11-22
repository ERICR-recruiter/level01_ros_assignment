#!/usr/bin/python3
import os
import launch, launch_ros
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
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
    ),
    launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time')}.items(),
  )

  spawn = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_testbed_gazebo, 'launch', 'spawn_testbed.launch.py'),
    )
  )
  
  rviz_config_dir = os.path.join(
    launch_ros.substitutions.FindPackageShare(package='testbed_navigation').find('testbed_navigation'),
    'rviz/navigation.rviz')
  
  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz_node',
    parameters=[{'use_sim_time': True}],
    arguments=['-d', LaunchConfiguration('rviz_config')]
  )

  return LaunchDescription([
    launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=rviz_config_dir,
                                            description='Absolute path to rviz config file'),
    launch.actions.DeclareLaunchArgument(name='rviz_config', default_value=LaunchConfiguration('rvizconfig'),
                                            description='Absolute path to rviz config file (alias of rvizconfig)'),
    launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='true',
                                            description='Use Gazebo /clock for robot_state_publisher'),
    state_pub,
    gazebo,
    spawn,
    rviz_node,
  ])
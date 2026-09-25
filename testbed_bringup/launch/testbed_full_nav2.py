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
  testbed_bringup = get_package_share_directory('testbed_bringup')
  pkg_testbed_description = get_package_share_directory('testbed_description')
  pkg_testbed_navigation = get_package_share_directory('testbed_navigation')
  nav2_directory= get_package_share_directory('nav2_bringup')
  testbed_navigation = get_package_share_directory('testbed_navigation')
  nav2_params = os.path.join(testbed_navigation, 'params', 'nav2_params.yaml')
  map_file = os.path.join(testbed_navigation,'params', 'testbed_world.yaml')

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

  map = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_testbed_navigation, 'launch', 'map_loader.launch.py'),
    ),
    launch_arguments={
      'use_rviz': 'false',
      'use_sim_time': 'true',
    }.items()
  )

  localization = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_testbed_navigation, 'launch', 'localization.launch.py'),
    ),
    launch_arguments={'use_sim_time': 'true'}.items()
  )
  
  rviz_config_dir = os.path.join(
    launch_ros.substitutions.FindPackageShare(package='testbed_description').find('testbed_description'),
    'rviz/full_bringup.rviz')
  
  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz_node',
    parameters=[{'use_sim_time': True}],
    arguments=['-d', LaunchConfiguration('rvizconfig')]
  )

  navigation_bringup = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(nav2_directory, 'launch', 'bringup_launch.py'),
    ),
    launch_arguments={
      'use_sim_time': 'true',
      'map': map_file,
      'params_file': nav2_params,
      'autostart': 'true'
    }.items()
  )
  

  return LaunchDescription([
    launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=rviz_config_dir,
                                            description='Absolute path to rviz config file'),
    state_pub,
    gazebo,
    spawn,
    map,
    localization,
    navigation_bringup,
    rviz_node,

  ])
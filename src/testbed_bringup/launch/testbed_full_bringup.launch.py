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


## inital rviz
inital_rviz_config_dir = os.path.join(
    launch_ros.substitutions.FindPackageShare(package='testbed_description').find('testbed_description'),
    'rviz/full_bringup.rviz')

## map_loader rviz
map_loader_rviz_config_dir = os.path.join(
  launch_ros.substitutions.FindPackageShare(package="testbed_navigation").find("testbed_navigation"),
  'rviz/map_rviz.rviz'
)

## global_localizatiion rviz
global_localization_rviz_config_dir = os.path.join(
  launch_ros.substitutions.FindPackageShare(package="testbed_localization").find("testbed_localization"),
  "rviz/global_localization.rviz"
)

## costmap
costmap_rviz_config_dir = os.path.join(
  launch_ros.substitutions.FindPackageShare(package="testbed_navigation").find("testbed_navigation"),
  "rviz/cost_map.rviz"
)
  

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

  ## launching controller for robot
  controller = IncludeLaunchDescription(
    os.path.join(
      get_package_share_directory("testbed_controller"),
      "launch",
      "controller.launch.py"
    ),
  )

  # ## map loader
  # map_loader = IncludeLaunchDescription(
  #   os.path.join(
  #     get_package_share_directory("testbed_mapping"),
  #     "launch",
  #     "map_loader.launch.py"
  #   ),
  # )


  ## launching localization 
  localization = IncludeLaunchDescription(
    os.path.join(
      get_package_share_directory("testbed_localization"),
      "launch",
      "global_localization.launch.py"
    ),
  )

  ## Navigation launching 
  navigation = IncludeLaunchDescription(
    os.path.join(
      get_package_share_directory("testbed_navigation"),
      "launch",
      "navigation.launch.py"
    ),
  )



  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz_node',
    parameters=[{'use_sim_time': True}],
    arguments=['-d', LaunchConfiguration('rvizconfig')]
  )

  return LaunchDescription([
    launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=costmap_rviz_config_dir,
                                            description='Absolute path to rviz config file'),
    state_pub,
    gazebo,
    spawn,
    rviz_node,
    controller,
    # map_loader,
    localization,
    navigation

  ])
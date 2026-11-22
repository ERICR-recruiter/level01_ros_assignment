# runs everything: gazebo + map + amcl + nav2 + rviz
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('testbed_navigation')
    gazebo_share = get_package_share_directory('testbed_gazebo')
    desc_share = get_package_share_directory('testbed_description')
    launch_dir = os.path.join(nav_share, 'launch')

    sim = LaunchConfiguration('sim')
    use_rviz = LaunchConfiguration('use_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    def include(path, args=None, condition=None):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(path),
            launch_arguments=(args or {}).items(),
            condition=condition)

    sim_args = {'use_sim_time': use_sim_time}

    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),

        include(os.path.join(gazebo_share, 'launch', 'spawn_playground.launch.py'),
                condition=IfCondition(sim)),
        include(os.path.join(desc_share, 'launch', 'robot_description.launch.py'),
                condition=IfCondition(sim)),
        include(os.path.join(gazebo_share, 'launch', 'spawn_testbed.launch.py'),
                condition=IfCondition(sim)),

        # wait a bit for the robot to spawn
        TimerAction(period=5.0, actions=[
            include(os.path.join(launch_dir, 'map_loader.launch.py'), sim_args),
            include(os.path.join(launch_dir, 'localization.launch.py'), sim_args),
            include(os.path.join(launch_dir, 'navigation.launch.py'), sim_args),
        ]),

        Node(
            package='rviz2', executable='rviz2', name='rviz2', output='log',
            arguments=['-d', os.path.join(nav_share, 'rviz', 'navigation.rviz')],
            parameters=[{'use_sim_time': use_sim_time}],
            condition=IfCondition(use_rviz)),
    ])

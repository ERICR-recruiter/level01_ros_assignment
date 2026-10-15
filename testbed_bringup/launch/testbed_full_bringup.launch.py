import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_bringup = get_package_share_directory('testbed_bringup')
    pkg_description = get_package_share_directory('testbed_description')
    pkg_gazebo = get_package_share_directory('testbed_gazebo')

    urdf_dir = os.path.join(pkg_description, 'urdf')
    helper_keywords = ['gazebo', 'lidar', 'camera', 'macro', 'sensor', 'material', 'include', 'wheel', 'chassis', 'ros2_control']
    candidate_files = []

    for file in os.listdir(urdf_dir):
        if file.endswith('.xacro') or file.endswith('.urdf'):
            if not any(keyword in file.lower() for keyword in helper_keywords):
                candidate_files.append(os.path.join(urdf_dir, file))

    if candidate_files:
        urdf_file = candidate_files[0]
    else:
        all_files = [os.path.join(urdf_dir, f) for f in os.listdir(urdf_dir) if f.endswith(('.xacro', '.urdf'))]
        urdf_file = sorted(all_files)[0]

    robot_description_config = xacro.process_file(urdf_file)
    robot_desc = robot_description_config.toxml()

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_desc}]
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'gazebo.launch.py')
        )
    )

    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'testbed_robot', '-z', '0.1'],
        output='screen'
    )

    delayed_spawn_entity = TimerAction(
        period=5.0,
        actions=[spawn_entity_node]
    )

    rviz_config_file = os.path.join(pkg_description, 'rviz', 'full_bringup.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo_launch,
        delayed_spawn_entity,
        rviz_node
    ])

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='spawn_entity',
            output='screen',
            arguments=[
                '-entity', 'testbed', '-topic', '/robot_description',
                '-x', '0', '-y', '5', '-z', '0', '-timeout', '120',
            ],
        ),
    ])

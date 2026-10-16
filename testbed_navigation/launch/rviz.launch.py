
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory(
        'testbed_description'
    )

    rviz_config = os.path.join(
        description_share,
        'rviz',
        'full_bringup.rviz'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[
            {'use_sim_time': True}
        ]
    )

    return LaunchDescription([
        rviz_node
    ])

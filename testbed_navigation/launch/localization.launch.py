import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('testbed_navigation')
    amcl_params = os.path.join(pkg_share, 'config', 'amcl_params.yaml')
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params]
    )
    return LaunchDescription([amcl_node])

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # The map from testbed_bringup's installed share folder (works on any machine)
    map_yaml = os.path.join(
        get_package_share_directory('testbed_bringup'), 'maps', 'testbed_world.yaml')

    # map_server parameters from this package's config folder
    map_params = os.path.join(
        get_package_share_directory('testbed_navigation'), 'config', 'map_server_params.yaml')

    # map_server: reads the YAML + PGM and publishes the map on /map
    map_server = Node(
        package='nav2_map_server', executable='map_server',
        name='map_server', output='screen',
        parameters=[map_params, {'yaml_filename': map_yaml}])

    # Lifecycle manager: configures and activates map_server
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_map', output='screen',
        parameters=[{'use_sim_time': True, 'autostart': True,
                     'node_names': ['map_server']}])

    return LaunchDescription([map_server, lifecycle_manager])

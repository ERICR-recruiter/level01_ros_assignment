import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node




def generate_launch_description():
    #default location for the map from the testbed_bringup package

    default_map = os.path.join(
        get_package_share_directory('testbed_bringup'),
        'maps',
        'testbed_world.yaml')

    #values to override from cmdline
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')

    #launch args
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value="true",
        description= 'use the gazebo sim clock'
    )

    declare_map = DeclareLaunchArgument(
        'map',
        default_value = default_map,
        description="full path to map yaml file"

    )


    #map server node
    map_server = Node(
        package='nav2_map_server',
        executable= 'map_server',
        name= 'map_server',
        output= 'screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            "yaml_filename": map_yaml,

        }])

    #lifecycle node to manage it
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable= 'lifecycle_manager',
        name= 'lifecycle_manager_map',
        output= 'screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            "autostart": True,
            'node_names': ['map_server'],
        }])

    return LaunchDescription([
        declare_use_sim_time,
        declare_map,
        map_server,
        lifecycle_manager,
    ])
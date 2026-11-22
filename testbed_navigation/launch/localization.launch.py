import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    # Retrieve launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    map_yaml_file = LaunchConfiguration('map')
    autostart = LaunchConfiguration('autostart')
    start_map_server_str = LaunchConfiguration('start_map_server').perform(context).lower()
    start_map_server = start_map_server_str in ['true', '1']

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    lifecycle_nodes = []
    actions = []

    # Optionally launch map_server if not already running via map_loader.launch.py
    if start_map_server:
        lifecycle_nodes.append('map_server')
        map_server_node = Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            emulate_tty=True,
            parameters=[
                params_file,
                {'yaml_filename': map_yaml_file, 'use_sim_time': use_sim_time}
            ],
            remappings=remappings
        )
        actions.append(map_server_node)

    # AMCL localization node
    lifecycle_nodes.append('amcl')
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        emulate_tty=True,
        parameters=[
            params_file,
            {'use_sim_time': use_sim_time}
        ],
        remappings=remappings
    )
    actions.append(amcl_node)

    # Lifecycle manager to transition AMCL (and optionally map_server) to active
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        emulate_tty=True,
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': autostart},
            {'node_names': lifecycle_nodes}
        ]
    )
    actions.append(lifecycle_manager_node)

    return actions


def generate_launch_description():
    pkg_testbed_nav = get_package_share_directory('testbed_navigation')
    pkg_testbed_bringup = get_package_share_directory('testbed_bringup')

    default_params_file = os.path.join(pkg_testbed_nav, 'config', 'amcl_params.yaml')
    default_map_path = os.path.join(pkg_testbed_bringup, 'maps', 'testbed_world.yaml')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to parameter file for AMCL'
    )

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to map yaml file to load (if start_map_server is true)'
    )

    declare_start_map_server_cmd = DeclareLaunchArgument(
        'start_map_server',
        default_value='false',
        description='Whether to start map_server inside localization launch (set true if not already running)'
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the localization stack'
    )

    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_start_map_server_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(OpaqueFunction(function=launch_setup))

    return ld

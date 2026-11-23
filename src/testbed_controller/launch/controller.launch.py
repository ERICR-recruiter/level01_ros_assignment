import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
)
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

from launch_xml.launch_description_sources import XMLLaunchDescriptionSource


def generate_launch_description():

    # Package directories
    controller_share = get_package_share_directory(
        'testbed_controller'
    )

    rosbridge_share = get_package_share_directory(
        'rosbridge_server'
    )

    # Configuration files
    topics_config = os.path.join(
        controller_share,
        'config',
        'twist_mux_topics.yaml'
    )

    locks_config = os.path.join(
        controller_share,
        'config',
        'twist_mux_locks.yaml'
    )

    # Website directory
    web_directory = os.path.join(
        controller_share,
        'web'
    )

    # Launch arguments
    web_port = LaunchConfiguration('web_port')
    websocket_port = LaunchConfiguration('websocket_port')

    # 1. Twist mux
    twist_mux_node = Node(
        package='twist_mux',
        executable='twist_mux',
        name='twist_mux',
        output='screen',

        parameters=[
            topics_config,
            locks_config
        ],

        remappings=[
            ('cmd_vel_out', '/cmd_vel')
        ]
    )

    # 2. Rosbridge WebSocket server
    rosbridge_launch_file = os.path.join(
        rosbridge_share,
        'launch',
        'rosbridge_websocket_launch.xml'
    )

    rosbridge_node = Node(
    package='rosbridge_server',
    executable='rosbridge_websocket',
    name='rosbridge_websocket',
    output='screen',

    parameters=[{
        'default_call_service_timeout': 5.0,
        'call_services_in_new_thread': True,
        'send_action_goals_in_new_thread': True,
    }],

    arguments=[
        '--ros-args',
        '-p', ['port:=', websocket_port],
        '-p', 'address:=0.0.0.0'
    ]
)

    # 3. Website HTTP server
    web_server = ExecuteProcess(
        cmd=[
            'python3',
            '-m',
            'http.server',
            web_port,
            '--bind',
            '0.0.0.0',
            '--directory',
            web_directory
        ],
        output='screen'
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'web_port',
            default_value='8000'
        ),

        DeclareLaunchArgument(
            'websocket_port',
            default_value='9090'
        ),

        twist_mux_node,

        rosbridge_node,

        web_server

    ])
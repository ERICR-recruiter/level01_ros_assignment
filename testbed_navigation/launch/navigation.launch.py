import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg_navigation = get_package_share_directory('testbed_navigation')

    params_file = ParameterFile(LaunchConfiguration('params_file'), allow_substs=True)
    use_sim_time = ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)
    autostart = ParameterValue(LaunchConfiguration('autostart'), value_type=bool)
    common_params = [params_file, {'use_sim_time': use_sim_time}]

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=common_params,
        remappings=[('cmd_vel', 'cmd_vel_nav')],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=common_params,
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=common_params,
        remappings=[('cmd_vel', 'cmd_vel_nav')],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=common_params,
    )

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=common_params,
        remappings=[
            ('cmd_vel', 'cmd_vel_nav'),
            ('cmd_vel_smoothed', 'cmd_vel'),
        ],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=common_params + [{'autostart': autostart}],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_navigation, 'config', 'nav2_params.yaml'),
            description='Absolute path to the Nav2 parameter file'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the simulation clock'),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Activate the navigation servers automatically'),
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        velocity_smoother,
        lifecycle_manager,
    ])

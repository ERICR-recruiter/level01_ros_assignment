import os 
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    nav2_params_file_path=os.path.join(get_package_share_directory('testbed_navigation'),'config','nav2_params.yaml')

    declare_use_sim_time_cmd=DeclareLaunchArgument(
        'use_sim_time',default_value='True',description='gz sim time'
    )
    declare_nav2_params_file_cmd= DeclareLaunchArgument(
        'params_file',default_value=nav2_params_file_path,description='navigation params file path'
    )

    start_controller_server= Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[LaunchConfiguration('params_file'),{'use_sim_time':LaunchConfiguration('use_sim_time')}]
    )
    start_planner_server= Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[LaunchConfiguration('params_file'),{'use_sim_time':LaunchConfiguration('use_sim_time')}]
    )
    start_behaviors_server= Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[LaunchConfiguration('params_file'),{'use_sim_time':LaunchConfiguration('use_sim_time')}]
    )
    start_bt_navigator_server= Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[LaunchConfiguration('params_file'),{'use_sim_time':LaunchConfiguration('use_sim_time')}]
    )
    start_lifecycle_manager_node= Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        parameters=[{'use_sim_time':LaunchConfiguration('use_sim_time')},{'autostart':True},{'node_names':['controller_server','planner_server','behavior_server','bt_navigator']}]
    )
    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_nav2_params_file_cmd,
        start_controller_server,
        start_planner_server,
        start_behaviors_server,
        start_bt_navigator_server,
        start_lifecycle_manager_node,
    ])
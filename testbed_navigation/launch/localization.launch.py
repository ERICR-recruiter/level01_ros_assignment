import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    default_params_path = os.path.join(
        get_package_share_directory('testbed_navigation'),
        'config',
        'amcl_params.yaml'
    )

    params_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_path
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[LaunchConfiguration('params_file'), {
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )

    lifecycle_manager_node = Node(  # brings amcl from unconfigured -> active
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': True,
            'node_names': ['amcl']
        }]
    )

    return LaunchDescription([
        params_arg,
        use_sim_time_arg,
        amcl_node,
        lifecycle_manager_node,
    ])
import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():

    amcl_param_file= os.path.join(get_package_share_directory('testbed_navigation'),'config','amcl_params.yaml')

    declare_use_sim_time_cmd= DeclareLaunchArgument('use_sim_time',default_value='True',description="gz sim time")
    declare_params_file_cmd=DeclareLaunchArgument('params_file', default_value=amcl_param_file,description='amcl params file path')

    start_amcl_node=Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[LaunchConfiguration('params_file'),{'use_sim_time': LaunchConfiguration('use_sim_time')}]

    )
    start_lifecycle_localization_node= Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        parameters=[{'use_sim_time':LaunchConfiguration('use_sim_time')},{'autostart':True},{'node_names':['amcl']}],
    )

    return LaunchDescription(
        [
            declare_use_sim_time_cmd,
            declare_params_file_cmd,
            start_amcl_node,
            start_lifecycle_localization_node,
        ]
    )
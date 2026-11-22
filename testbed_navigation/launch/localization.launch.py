import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import GroupAction, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
        nav_dir = get_package_share_directory('testbed_navigation')
        use_sim_time = True
        log_level = 'info'
        params_file = LaunchConfiguration('params_file')

        lifecycle_nodes = ['amcl']
        remappings = [('/tf', 'tf'),
              ('/tf_static', 'tf_static')]

        declare_params_file_cmd = DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(nav_dir, 'config', 'amcl_params.yaml'),
            description='Full path to the AMCL parameters file'
        )



        load_nodes = GroupAction(
            actions=[
            Node(
                package='nav2_amcl',
                executable='amcl',
                name='amcl',
                output='screen',
                respawn=True,
                respawn_delay=2.0,
                parameters=[params_file, {'use_sim_time': use_sim_time}],                
                arguments=['--ros-args', '--log-level', log_level],
                remappings=remappings),

            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_acml',
                output='screen',
                arguments=['--ros-args', '--log-level', log_level],
                parameters=[{'use_sim_time': use_sim_time},
                            {'autostart': True},
                            {'node_names': lifecycle_nodes}]
        )
        ]
)
        

        ld = LaunchDescription()
        ld.add_action(declare_params_file_cmd)
        ld.add_action(load_nodes)
        return ld
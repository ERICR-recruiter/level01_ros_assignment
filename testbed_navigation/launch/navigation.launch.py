import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node




def generate_launch_description():
        bringup_dir = get_package_share_directory('testbed_bringup')
        use_sim_time = True
        map_yaml_file = os.path.join(bringup_dir, 'maps', 'testbed_world.yaml')       
        log_level = 'info'

        lifecycle_nodes = ['map_server']
        remappings = [('/tf', 'tf'),
              ('/tf_static', 'tf_static')]


        load_nodes = GroupAction(
            actions=[
                Node(
                    package='nav2_map_server',
                    executable='map_server',
                    name='map_server',
                    output='screen',
                    respawn=False,
                    respawn_delay=2.0,
                    parameters=[
                        {'use_sim_time': use_sim_time},
                        {'yaml_filename': map_yaml_file}
                    ],
                    arguments=['--ros-args', '--log-level', log_level],
                    remappings=remappings),
                Node(
                    package='nav2_lifecycle_manager',
                    executable='lifecycle_manager',
                    name='lifecycle_manager_localization',
                    output='screen',
                    arguments=['--ros-args', '--log-level', log_level],
                    parameters=[{'use_sim_time': use_sim_time},
                            {'autostart': True},
                            {'node_names': lifecycle_nodes}])
            ]

        )

        ld = LaunchDescription()
        ld.add_action(load_nodes)
        return ld
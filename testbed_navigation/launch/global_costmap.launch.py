from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution

def generate_launch_description():

    nav2_params = PathJoinSubstitution([
        FindPackageShare('testbed_navigation'),
        'config',        
        'nav2_params.yaml'
    ])

    global_costmap = Node(
        package='nav2_costmap_2d',
        executable='nav2_costmap_2d',
        namespace='global_costmap',
        name='costmap',
        output='screen',
        parameters=[nav2_params]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_global_costmap',
        output='screen',
        parameters=[{'use_sim_time': True},
                    {'autostart': True},
                    {'bond_timeout': 15.0},
                    {'node_names': ['/costmap/costmap']}]
    )

    return LaunchDescription([
        global_costmap,
        lifecycle_manager
    ])
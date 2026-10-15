import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    testbed_gazebo_dir = get_package_share_directory('testbed_gazebo')
    testbed_description_dir = get_package_share_directory('testbed_description')

    world_file = os.path.join(testbed_gazebo_dir, 'worlds', 'testbed_world.world')

    gazebo_model_path = SetEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        os.path.join(testbed_gazebo_dir, 'models') + ':' + testbed_description_dir
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )

    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    return LaunchDescription([
        gazebo_model_path,
        gzserver,
        gzclient
    ])

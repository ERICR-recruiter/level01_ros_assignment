from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    gazebo_share = get_package_share_directory("gazebo_ros")
    testbed_share = get_package_share_directory("testbed_gazebo")

    world = LaunchConfiguration("world")

    return LaunchDescription([
        DeclareLaunchArgument(
            "world",
            default_value=f"{testbed_share}/worlds/testbed_playground.world",
            description="Gazebo world file to load...",
        ),
        SetEnvironmentVariable(
            "GAZEBO_MODEL_PATH",
            f"{testbed_share}/models",
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                f"{gazebo_share}/launch/gazebo.launch.py"
            ),
            launch_arguments={"world": world}.items(),
        ),
    ])

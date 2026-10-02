import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    nav_launch = os.path.join(
        get_package_share_directory('testbed_navigation'), 'launch')

    def include(name):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav_launch, name)))

    return LaunchDescription([
        include('map_loader.launch.py'),
        include('localization.launch.py'),
        include('navigation.launch.py'),
    ])
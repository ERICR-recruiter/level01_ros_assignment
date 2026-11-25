#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    bringup_share = get_package_share_directory('testbed_bringup')
    navigation_share = get_package_share_directory('testbed_navigation')

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                bringup_share,
                'launch',
                'testbed_full_bringup.launch.py'
            )
        )
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'localization.launch.py'
            )
        )
    )
    
    navigation = IncludeLaunchDescription(
             PythonLaunchDescriptionSource(
                  os.path.join(
                       navigation_share,
                       'launch',
                       'navigation.launch.py'
                       )
                  )
             )

    return LaunchDescription([
        simulation,
        localization,
        navigation,
    ])

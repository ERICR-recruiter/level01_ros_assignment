
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    bringup_share = get_package_share_directory('testbed_bringup')
    navigation_share = get_package_share_directory('testbed_navigation')

    # 1. Start Gazebo and robot bringup
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                bringup_share,
                'launch',
                'testbed_full_bringup.launch.py'
            )
        )
    )

    # 2. Start the map server after bringup
    map_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'map_loader.launch.py'
            )
        )
    )

    # 3. Start localization after the map server
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'localization.launch.py'
            )
        )
    )

    # 4. Start Nav2 after localization
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'navigation.launch.py'
            )
        )
    )

    # 5. Start RViz only after the other launch files have started
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'rviz.launch.py'
            )
        )
    )

    return LaunchDescription([
        bringup_launch,

        TimerAction(
            period=5.0,
            actions=[
                map_launch,

                TimerAction(
                    period=5.0,
                    actions=[
                        localization_launch,

                        TimerAction(
                            period=8.0,
                            actions=[
                                navigation_launch,

                                TimerAction(
                                    period=5.0,
                                    actions=[
                                        rviz_launch
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ])

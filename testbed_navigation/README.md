# Testbed Navigation — ERIC Robotics Level 1

## Overview

Modular ROS 2 Humble navigation implementation for the
Testbed-T1.0.0 robot using Gazebo Classic and Nav2.

The implementation launches the Nav2 components independently,
without using nav2_bringup.

## Architecture

Gazebo Robot
    |
    +-- /scan --> AMCL --> map to odom TF
    |
    +-- /odom
    |
    +-- /cmd_vel

ComputePathToPose
    |
    v
Planner Server
    |
    v
FollowPath
    |
    v
Controller Server
    |
    v
Robot Motion

## Components

- map_loader.launch.py: Map Server
- localization.launch.py: AMCL
- navigation.launch.py: Planner, Controller, Behavior Server,
  BT Navigator and lifecycle management
- manual_navigation_test.py: Manual action-based navigation client

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic
- Nav2
- RViz2

## Build

From the workspace root:

    colcon build --symlink-install
    source install/setup.bash

## Launch

Open separate terminals and source the workspace in each.

Terminal 1:

    ros2 launch testbed_bringup testbed_full_bringup.launch.py

Terminal 2:

    ros2 launch testbed_navigation map_loader.launch.py

Terminal 3:

    ros2 launch testbed_navigation localization.launch.py

Terminal 4:

    ros2 launch testbed_navigation navigation.launch.py

## Navigation Test

    ros2 run testbed_navigation manual_navigation_test.py 1.0 5.0 --yaw 0.0

Return:

    ros2 run testbed_navigation manual_navigation_test.py 0.0 5.0 --yaw 0.0

## Testing and Limitations

The global planner and FollowPath action client were tested
successfully in Gazebo.

Forward and return navigation actions have succeeded.

Intermittent near-goal controller stalls were also observed.
Goal accuracy should be verified using map-frame TF and
Gazebo ground-truth measurements.

The original LiDAR range was 1.5 m. An experimental 8 m
range was used to investigate localization performance.

See ../bugs_fixed.txt for debugging details.

## Independent goal-accuracy verification

After a `FollowPath` success, check the Gazebo ground-truth position and the
AMCL map estimate, which may disagree:

    ros2 run testbed_navigation report_pose_accuracy.py 0.0 5.0 --yaw 0.0

The reporter exits nonzero if the final estimated or physical goal pose is out
of tolerance. The script assumes the corrected Gazebo world and occupancy map
are aligned; verify this assumption after any environment changes.

Run three round trips and save the results to a log:

    ros2 run testbed_navigation run_navigation_regression.sh 3

For the cause of the map/world mismatch, recovery from a previous launch, and
limitations of the offline checks, see `../RELIABILITY_FIXES.md`.

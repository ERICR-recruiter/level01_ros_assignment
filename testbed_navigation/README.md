# Testbed Navigation

## Overview

This package implements modular ROS 2 Humble navigation for the
Testbed robot using Nav2.

## Package Structure

- launch/map_loader.launch.py
- launch/localization.launch.py
- launch/navigation.launch.py
- config/amcl_params.yaml
- config/nav2_params.yaml

## Architecture

The navigation system is divided into three stages:

1. Map loading using Nav2 Map Server.
2. Robot localization using AMCL.
3. Path planning and navigation using Nav2.

## Dependencies

- ROS 2 Humble
- Nav2
- AMCL
- Nav2 Map Server
- Nav2 Planner
- Nav2 Controller
- Nav2 Behavior Server
- Nav2 BT Navigator
- Nav2 Lifecycle Manager

## Robot Frames

- map
- odom
- base_footprint
- lidar_link_1

## Important Topics

- /map
- /scan
- /odom
- /cmd_vel
- /amcl_pose
- /initialpose
- /goal_pose
- /plan
- /global_costmap/costmap
- /local_costmap/costmap

## Build

From the workspace root:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash

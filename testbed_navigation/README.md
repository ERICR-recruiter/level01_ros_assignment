# Testbed Navigation

## Overview

This package provides separate ROS 2 launch files for map hoading, AMCL localization, and Nav2 navigation for the Testbed-T1.0.0 robot.

## Package structure

- `launch/map_server.launch.py`: starts the map server.
- `launch/localization.launch.py`: starts AMCL localization.
- `launch/navigation.launch.py`: starts Nav2 navigation components.
- `config/nav2_params.yaml`: contains navigation and costmap parameters.

## Requirements

- ROS 2 Humble
- Gazebo and the supplied testbed packages
- Nav2

## Build

From the workspace root, inside the ROS 2 Humble environment:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Launch sequence

Run each launch command in a separate terminal in the same Docker container. Source ROS 2 Humble and the workspace setup file in each terminal.

1. Start the simulation using the launch file supplied by `testbed_bringup`.
2. Start the map server: `ros2 launch testbed_navigation map_server.launch.py`
3. Start localization: `ros2 launch testbed_navigation localization.launch.py`
4. Set the robot's initial pose using RViz or publish a geometry_msgs/msg/PoseWithCovarianceStamped message to /initialpose.
5. Start navigation: ros2 launch testbed_navigation navigation.launch.py
6. Send a goal using RViz or the /navigate_to_pose action.

Do not launch multiple instances of the simulation, map server, localization, or navigation stack simultaneously.

## Verification
Useful checks:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /map --once
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 action list
```

A valid initial pose and required TF transforms are needed before navigation goals can succeed. Record the actual results of each test in the project report.

## Navigation Configuration

The navigation stack is configured manually using ROS2 Nav2 components.

The main components used are:

- `nav2_map_server` for loading the provided occupancy map
- `nav2_amcl` for localization
- `nav2_planner` with NavFn as the global planner
- `nav2_controller` with DWB as the local controller
- Global and local costmaps using LaserScan obstacle data
- `nav2_behaviors` for recovery behaviors
- `nav2_bt_navigator` for behavior-tree based navigation
- Nav2 lifecycle managers for automatic node configuration and activation

The robot uses:

- `map` as the global frame
- `odom` as the odometry frame
- `base_footprint` as the robot base frame
- `/scan` for LaserScan data
- `/odom` for odometry

## Build

From the workspace:

```bash
cd ~/assignment_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash

# Testbed Navigation

This package contains my ROS2 Humble Nav2 implementation for the ERIC Robotics Level 1 ROS2 Navigation Assignment.

The main aim was to configure the required Nav2 components manually instead of directly using the `nav2_bringup` launch files.

## Approach

I divided the navigation setup into three separate parts:

1. Map Loading
2. Localization
3. Navigation

Separate launch files are used for each part so that every component can be started and tested independently.

## Package Structure

```text
testbed_navigation/
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
├── CMakeLists.txt
├── package.xml
└── README.md

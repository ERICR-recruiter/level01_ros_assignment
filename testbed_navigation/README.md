# ROS 2 Navigation – ERIC Assignment

## 1. Project Overview

This package implements a manually configured ROS 2 Navigation (Nav2) stack for the ERIC mobile robot simulation.

The robot operates in Gazebo Classic and uses RViz for map visualization, localization monitoring and goal selection.

The navigation system uses:
- Nav2 Map Server for loading the occupancy map.
- AMCL for robot localization.
- NavFn for global path planning.
- DWB for local path planning and velocity control.
- Behavior Server for recovery behaviours.
- BT Navigator for navigation task execution.
- Lifecycle Manager for managing Nav2 node states.

## 2. Software Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic 11
- RViz2
- Navigation2 packages

## 3. Package Structure

```text
testbed_navigation/
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
├── screenshots/
├── CMakeLists.txt
├── package.xml
└── README.md
```

## 4. Build Instructions

Navigate to the workspace:

```bash
cd ~/ERIC_ROS_Assignment
```

Source ROS 2 Humble:

```bash
source /opt/ros/humble/setup.bash
```

Build the workspace:

```bash
colcon build --symlink-install
```

Source the workspace:

```bash
source install/setup.bash
```

## 5. Launch Instructions

Start each component in a separate terminal.

### Terminal 1 – Gazebo and RViz

```bash
cd ~/ERIC_ROS_Assignment
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### Terminal 2 – Map Server

```bash
cd ~/ERIC_ROS_Assignment
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch testbed_navigation map_loader.launch.py
```

### Terminal 3 – AMCL Localization

```bash
cd ~/ERIC_ROS_Assignment
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch testbed_navigation localization.launch.py
```

### Terminal 4 – Nav2 Navigation

```bash
cd ~/ERIC_ROS_Assignment
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```

## 6. Initial Pose Configuration

After starting the map server and AMCL, provide the robot's initial estimated pose using RViz's **2D Pose Estimate** tool.

Steps:

1. Set RViz Fixed Frame to `map`.
2. Select `2D Pose Estimate`.
3. Click the robot's approximate location on the map.
4. Drag the arrow to indicate its orientation

## 7. Screenshots

The following screenshots demonstrate the implementation:

1. `screenshots/01_gazebo_robot.png` – Gazebo robot simulation.
2. `screenshots/02_rviz_map.png` – RViz map and robot visualization.
3. `screenshots/03_amcl_localization.png` – AMCL localization activation.
4. `screenshots/04_nav2_active.png` – Nav2 lifecycle activation.

## 8. Demonstration Video

A demonstration video of the ROS 2 navigation implementation can be added here.

**Video Link:** To be added.

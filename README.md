# Level 1: ROS 2 Navigation Assignment

## Overview

This repository contains the completed ROS 2 navigation implementation for the ERIC Robotics Level 1 assignment using the Testbed-T1.0.0 robot.

The assignment required building a navigation workflow manually with individual Nav2 components instead of using the single `nav2_bringup` launch package. The final implementation provides:

- Gazebo simulation and RViz visualization
- Map loading using Nav2 Map Server
- AMCL-based localization
- Global path planning using NavFn
- Local path following using Regulated Pure Pursuit
- Local and global costmaps
- Behavior Server and BT Navigator
- Automatic AMCL initialization at the simulation spawn pose
- Navigation to multiple goals

The implementation was developed and tested with ROS 2 Humble on Ubuntu 22.04 and Gazebo Classic 11.10.2.
---

Explanation Video: https://drive.google.com/file/d/14oWKHtbTVp4KpP5GUbqZeqg8gsd4fCJ_/view?usp=sharing


<img width="1573" height="997" alt="Screenshot from 2026-09-22 15-31-30" src="https://github.com/user-attachments/assets/a961a4f8-fc29-4618-9d57-9bf69a83c86e" />

<img width="1849" height="1164" alt="Screenshot from 2026-09-22 15-31-45" src="https://github.com/user-attachments/assets/a7409bb2-3fc2-4254-8ef1-1189fa8e9f02" />

---

## Assignment Requirements Addressed

The completed project addresses the main assignment requirements:

1. Identify and fix bugs in the provided starter packages.
2. Document the identified bugs and fixes in `BUGS_FIXED.txt`.
3. Create a new `testbed_navigation` package using `ament_cmake`.
4. Manually configure the map server and localization workflow.
5. Manually configure the Nav2 planner, controller, costmaps, behavior server, and BT navigator.
6. Provide individual launch files for map loading, localization, and navigation.
7. Test localization in RViz and navigation to goals in Gazebo.
8. Document the implementation, setup procedure, and challenges.

---

## Repository Structure

```text
level01_ros_assignment/
├── BUGS_FIXED.txt
├── README.md
├── help.md
│
├── testbed_bringup/
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── launch/
│   └── maps/
│
├── testbed_description/
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── launch/
│   ├── meshes/
│   ├── rviz/
│   └── urdf/
│
├── testbed_gazebo/
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── launch/
│   ├── models/
│   └── worlds/
│
└── testbed_navigation/
    ├── CMakeLists.txt
    ├── package.xml
    ├── config/
    │   ├── amcl_params.yaml
    │   └── nav2_params.yaml
    └── launch/
        ├── map_loader.launch.py
        ├── localization.launch.py
        └── navigation.launch.py
```

---

## Requirements

The tested environment is:

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic 11.10.2
- RViz2
- Nav2 packages
- `colcon`

A ROS 2 Humble installation should be available before building this repository.

Useful ROS 2 packages for this project include:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-xacro \
  ros-humble-rviz2 \
  ros-humble-tf2-tools
```

If the system already contains ROS 2 Humble, Gazebo, RViz2, and Nav2, only missing packages need to be installed.

---

## Getting the Repository

Create a ROS 2 workspace and clone the repository into `src`:

```bash
mkdir -p ~/assignment_ws/src
cd ~/assignment_ws/src

git clone <your-fork-url> level01_ros_assignment
```

For example:

```bash
cd ~/assignment_ws/src
# git clone https://github.com/<your-github-username>/level01_ros_assignment.git
```

Then build the workspace:

```bash
cd ~/assignment_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

For subsequent terminals, source both ROS 2 and the workspace:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
```

---

# Running the Complete System

The final implementation is intentionally split into separate launch files so that each part of the navigation workflow can be started and tested independently.

There are four launch files involved in the complete workflow:

1. `testbed_full_bringup.launch.py` - Gazebo/RViz simulation
2. `map_loader.launch.py` - map server and lifecycle manager
3. `localization.launch.py` - AMCL localization
4. `navigation.launch.py` - Nav2 navigation stack

Open four terminals and source the workspace in each terminal.

<img width="1847" height="1162" alt="Screenshot from 2026-09-22 15-29-34" src="https://github.com/user-attachments/assets/d8bab4bb-fc1d-4c44-beef-8b794534558d" />

---

## 1. Start the Simulation

Terminal 1:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

This starts the Testbed-T1.0.0 simulation in Gazebo and the configured RViz environment.

The simulation publishes the robot's sensors and motion data, including:

- `/scan`
- `/odom`
- TF from `odom` to `base_footprint`

The robot is spawned at approximately:

```text
x = 0.0 m
y = 5.0 m
yaw = 0.0 rad
```

The automatic AMCL initialization described below assumes this simulation spawn pose.

---

## 2. Start the Map Server

Terminal 2:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation map_loader.launch.py
```

This launch file manually starts:

- `nav2_map_server`
- Nav2 lifecycle manager

The map is loaded from:

```text
testbed_bringup/maps/testbed_world.yaml
```

After startup, the map is available on `/map`.

---

## 3. Start Localization

Terminal 3:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation localization.launch.py
```

This launch file manually starts:

- `nav2_amcl`
- Nav2 lifecycle manager for AMCL

### Automatic Initial Pose

AMCL is configured to initialize automatically at the known simulation spawn pose:

```text
x = 0.0
y = 5.0
z = 0.0
yaw = 0.0
```

Therefore, no manual `/initialpose` command is required for the final setup.

The configuration is in:

```text
testbed_navigation/config/amcl_params.yaml
```

After AMCL starts, verify localization with:

```bash
ros2 topic echo /amcl_pose --once
```

The reported pose should be close to the robot's actual pose in the map.

---

## 4. Start Navigation

Terminal 4:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```

This manually starts the Nav2 navigation components:

- Planner Server
- Controller Server
- Behavior Server
- BT Navigator
- Local costmap
- Global costmap
- Navigation lifecycle manager

No `nav2_bringup` navigation launch file is used.

---

# Navigation Configuration

The navigation configuration is stored in:

```text
testbed_navigation/config/nav2_params.yaml
```

## Global Planner

The global planner is:

```text
NavFn
```

configured as:

```yaml
plugin: "nav2_navfn_planner/NavfnPlanner"
```

## Local Controller

The local controller is:

```text
Regulated Pure Pursuit
```

configured as:

```yaml
plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
```

It uses velocity regulation, lookahead control, collision checking, and rotate-to-heading behavior.

## Costmaps

### Global Costmap

The global costmap uses:

- Static layer
- Obstacle layer
- Inflation layer

The global frame is:

```text
map
```

### Local Costmap

The local costmap uses:

- Obstacle layer
- Inflation layer
- Rolling window

The local frame is:

```text
odom
```

Both costmaps use the robot's LiDAR on:

```text
/scan
```

The LiDAR was configured with a 5 m maximum range and the costmap obstacle/ray-tracing limits were configured accordingly.

<img width="1847" height="1162" alt="Screenshot from 2026-09-22 15-30-58" src="https://github.com/user-attachments/assets/719e9fdc-6734-4a9e-a26a-e373d1ac6bd7" />


---

# Sending a Navigation Goal

After all four launch files are running and AMCL has initialized, a navigation goal can be sent from RViz using the Nav2 **2D Goal Pose** tool.

The expected workflow is:

```text
Gazebo simulation
      ↓
Map Server
      ↓
AMCL localization
      ↓
Nav2 planner
      ↓
Nav2 controller
      ↓
/cmd_vel
      ↓
Robot reaches goal
```

Multiple navigation goals were tested during development, including goals requiring turning, path following, and recovery behavior. The final configuration successfully reached the tested goals without navigation warnings or errors.

<img width="1849" height="1164" alt="Screenshot from 2026-09-22 15-32-01" src="https://github.com/user-attachments/assets/5cbdaeef-9327-4e6d-a8f0-c5457bb5230d" />

---

# What Was Implemented

## 1. Starter Code Debugging

The provided starter packages contained intentional issues. The identified problems and their fixes are documented separately in:

```text
BUGS_FIXED.txt
```

The verified fixes included:

- Correcting the missing `()` in `ament_package()`.
- Correcting the map image path in `testbed_world.yaml`.
- Installing the `maps` directory from `testbed_bringup`.
- Installing the Gazebo `models` directory from `testbed_gazebo`.

These fixes allow the original simulation and its resources to build and run correctly.

## 2. Navigation Package

A new package called:

```text
testbed_navigation
```

was created using `ament_cmake`.

The package separates the navigation workflow into individual launch files and parameter files rather than hiding the complete workflow inside a single launch command.

## 3. Manual Map Loading

A dedicated map loader was implemented using Nav2 Map Server and its lifecycle manager.

## 4. AMCL Localization

AMCL was configured for the differential-drive robot using the `/scan` LiDAR data, `map`, `odom`, and `base_footprint` frames.

The AMCL configuration was tuned and verified experimentally. Important parameters include:

- 1000 to 3000 particles
- 180 laser beams
- 0.05 m translational update threshold
- 0.05 rad angular update threshold
- likelihood-field laser model

Automatic initial pose support was added so that the robot can initialize without manually publishing to `/initialpose` every time the simulation starts.

## 5. LiDAR Configuration

The Gazebo LiDAR configuration was extended from the original short range to a 5 m range so that more of the environment is visible to localization and obstacle processing.

The Nav2 local and global costmaps were updated to use the same effective obstacle and ray-tracing range.

## 6. Manual Navigation Stack

Instead of using `nav2_bringup`, the required navigation components were launched directly:

```text
planner_server
controller_server
behavior_server
bt_navigator
local_costmap
 global_costmap
```

A Nav2 lifecycle manager coordinates activation of these nodes.

## 7. Simulation Time Handling

All navigation components are configured to use Gazebo simulation time. During testing, a planner-side simulation-time mismatch was identified and corrected.

## 8. Controller and Progress Tuning

The final controller configuration uses Regulated Pure Pursuit. The progress checker and goal checker were tuned so that normal turning and short-distance movement do not trigger unnecessary recovery behavior.

---

# Challenges and Debugging

Several problems were encountered during implementation and were resolved systematically.

### Build and installation issues

The starter packages contained CMake installation problems that prevented required files from appearing in the installed workspace. These were corrected so that maps and Gazebo models are installed correctly.

### Map loading

The map server initially referenced an invalid map image path. Correcting the YAML path allowed the map to load successfully.

### AMCL configuration

The initial AMCL configuration used a shorter LiDAR range, fewer laser beams, fewer particles, and larger update thresholds. The configuration was updated and rebuilt so that the running node uses the final values.

### NavFn plugin naming

The installed Humble NavFn plugin exposes the class as:

```text
nav2_navfn_planner/NavfnPlanner
```

The planner configuration was corrected to use the available plugin identifier.

### Progress checker behavior

The controller's progress checker was tuned after testing showed unnecessary progress failures during navigation. The final configuration allows normal turning and motion without immediately triggering recovery actions.

---

# Final Result

The completed system provides a modular ROS 2 navigation workflow:

```text
Testbed-T1.0.0 Simulation
          │
          ├── Gazebo
          ├── LiDAR /scan
          └── Odometry /odom
                   │
                   ▼
             Map Server
                   │
                   ▼
                AMCL
                   │
              map → odom
                   │
                   ▼
          ┌─────────────────┐
          │    Nav2 Stack   │
          │                 │
          │ Global Planner  │
          │ Local Controller│
          │ Costmaps        │
          │ BT Navigator    │
          │ Behaviors       │
          └─────────────────┘
                   │
                   ▼
                 /cmd_vel
                   │
                   ▼
             Robot Navigation
```

The final implementation was tested from a fresh startup sequence. Localization converged correctly, odometry was consistent with the simulated robot pose, and navigation goals were successfully executed.

---

## Quick Start Summary

For a quick run after the workspace has been built:

### Terminal 1

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### Terminal 2

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation map_loader.launch.py
```

### Terminal 3

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation localization.launch.py
```

### Terminal 4

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```

Once all four are active, use RViz's **2D Goal Pose** tool to send a navigation goal.

No manual `/initialpose` command is required in the final configuration because AMCL initializes automatically at the robot's configured simulation spawn pose.

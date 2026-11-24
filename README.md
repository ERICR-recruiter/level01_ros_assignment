# ROS 2 Autonomous Mobile Robot (AMR) Navigation

### ERIC Robotics Testbed T1.0.0 | ROS 2 Navigation Assignment

A modular ROS 2-based autonomous mobile robot simulation project focused on robot description, Gazebo simulation, mapping, localization, motion control, and autonomous navigation using Nav2.

The project follows a modular package architecture, separating robot description, simulation, control, mapping, localization, and navigation into independent ROS 2 packages.

---

## 🎥 Project Demonstration

**Watch the ROS 2 Autonomous Mobile Robot simulation and navigation demonstration.**

[![ROS 2 AMR Project Demonstration](https://img.youtube.com/vi/SvJPw2QtG_k/maxresdefault.jpg)](https://www.youtube.com/watch?v=SvJPw2QtG_k)

▶ **[Watch Full Project Demonstration on YouTube](https://youtu.be/SvJPw2QtG_k)**

---

The demonstration video is available in the `testbed_media` directory.

---

## 🚀 Project Overview

This project implements a simulated differential-drive mobile robot using ROS 2 and Gazebo.

The development focuses on understanding and implementing the core components of an autonomous mobile robot system.

### Key Components

- **Robot Description:** URDF/Xacro-based robot model and sensor configuration.
- **Simulation:** Gazebo environment and robot spawning.
- **Robot Control:** Differential-drive control and controller configuration.
- **Web Controller:** Browser-based joystick interface for manual robot control.
- **Mapping:** Environment mapping using SLAM Toolbox.
- **Localization:** Robot localization using AMCL.
- **Navigation:** Autonomous path planning and motion control using Nav2.
- **Visualization:** RViz2 for robot visualization, maps, TF frames, and navigation data.

---

## 🛠️ Development Environment

| Component | Version |
|---|---|
| Operating System | Ubuntu 22.04 |
| ROS 2 | Humble |
| Build System | Colcon |
| Robot Simulator | Gazebo |
| Visualization | RViz2 |
| Programming Language | Python |
| Robot Description | URDF / Xacro |
| Navigation Framework | Nav2 |
| Mapping | SLAM Toolbox |
| Localization | AMCL |

---

## 📂 Workspace Architecture

The workspace is organized into modular ROS 2 packages.

```text
ros_nav2_assignment_ws/
│
└── src/
    │
    ├── testbed_bringup/
    │   ├── launch/
    │   ├── maps/
    │   └── rviz/
    │
    ├── testbed_controller/
    │   ├── config/
    │   ├── launch/
    │   └── web/
    │
    ├── testbed_description/
    │   ├── launch/
    │   ├── meshes/
    │   ├── rviz/
    │   └── urdf/
    │
    ├── testbed_gazebo/
    │   ├── launch/
    │   ├── models/
    │   └── worlds/
    │
    ├── testbed_localization/
    │   ├── config/
    │   ├── launch/
    │   └── rviz/
    │
    ├── testbed_mapping/
    │   ├── config/
    │   ├── launch/
    │   └── rviz/
    │
    ├── testbed_media/
    │   ├── BUGS_AND_DEBUGGING.md
    │   ├── README.md
    │   └── Demonstration Video
    │
    └── testbed_navigation/
        ├── behavior_tree/
        ├── config/
        ├── config1/
        ├── launch/
        ├── rviz/
        └── testbed_navigation/
```

---

## 📦 ROS 2 Package Description

| Package | Responsibility |
|---|---|
| `testbed_description` | Robot model, URDF/Xacro, meshes, and TF-related launch configurations. |
| `testbed_gazebo` | Gazebo simulation worlds, robot models, and spawning launch files. |
| `testbed_controller` | Robot controllers, Twist Mux configuration, and web-based joystick interface. |
| `testbed_mapping` | SLAM Toolbox configuration and map generation. |
| `testbed_localization` | AMCL configuration and global localization. |
| `testbed_navigation` | Nav2 configuration, behavior trees, planner, controller, and waypoint following. |
| `testbed_bringup` | Main system bringup, map files, and integrated launch configuration. |

---

## ⚙️ Build Instructions

### 1. Source ROS 2 Humble

```bash
source /opt/ros/humble/setup.bash
```

### 2. Navigate to the workspace

```bash
cd ~/ros_nav2_assignment_ws
```

### 3. Build the workspace

```bash
colcon build --symlink-install
```

### 4. Source the workspace

```bash
source install/setup.bash
```

---

## ▶️ Launch the System

Launch the complete testbed using:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

This is the main integrated bringup launch file for the testbed.

---

## 🔍 Debugging and Development Notes

During development, several issues were investigated and addressed across different ROS 2 components.

Some of the debugging areas included:

- CMake and XML syntax corrections.
- URDF/Xacro parameter handling.
- TF timestamp warnings and duplicate transform publishers.
- RViz map subscription and QoS durability configuration.
- Circular package dependencies during Colcon builds.
- Map server lifecycle transition failures.
- Nav2 controller and planner parameter tuning.
- Robot rotation and goal-reaching behaviour.

Detailed debugging observations, errors, and corrective actions are documented here:

[View BUGS_AND_DEBUGGING.md](src/testbed_media/BUGS_AND_DEBUGGING.md)

---

## 📁 Project Media

The `testbed_media` directory contains supporting development materials:

- Robot TF tree visualizations.
- TF frame PDF reports.
- Debugging documentation.
- Robot simulation demonstration video.

---

## 🎯 Project Objective

The primary objective of this project is to understand the development and integration of an autonomous mobile robot using ROS 2.

The project provides practical experience with:

- Modular ROS 2 package development.
- Robot description and simulation.
- Sensor and TF integration.
- Differential-drive robot control.
- SLAM and localization.
- Global and local path planning.
- Autonomous navigation using Nav2.
- Debugging and configuration of distributed ROS 2 nodes.

---

## 📌 Current Development Status

The project is under active development.

Core workspace packages and simulation components have been developed. Mapping, localization, and autonomous navigation configurations are being integrated and tested.

Navigation controller and planner parameters are undergoing iterative tuning to improve robot movement, path following, and goal-reaching behaviour.

---

**Project:** ERIC Robotics Testbed T1.0.0  
**Platform:** ROS 2 Humble  
**Build System:** Colcon  
**Simulator:** Gazebo  
**Visualization:** RViz2

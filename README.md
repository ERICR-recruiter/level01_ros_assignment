# Level 1 ROS2 Navigation Assignment

## 1. Overview

This project implements a ROS 2 Navigation2 (Nav2) stack manually for the
provided testbed robot environment.

The objective of the assignment is to build and demonstrate a complete
navigation pipeline without using the `nav2_bringup` package.

The implemented system contains:

- Map Server
- AMCL localization
- NavFn global planner
- DWB local controller
- Global costmap
- Local costmap
- Behavior Server
- Behavior Tree Navigator
- Lifecycle Managers
- TF transformation tree
- RViz2 visualization
- Gazebo simulation

The robot receives a navigation goal from RViz2, computes a global path,
generates local velocity commands and moves toward the goal using the
differential-drive controller.

---

# 2. System Environment

## Operating System

- Ubuntu 22.04 LTS

## ROS 2 Distribution

- ROS 2 Humble

## Simulation

- Gazebo

## Visualization

- RViz2

## Navigation Framework

- Navigation2 (Nav2)

---

# 3. Package Structure

The repository contains the following main packages:

```text
level01_ros_assignment/
│
├── README.md
├── STARTER_BUGS.md
│
├── testbed_bringup/
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── launch/
│   └── maps/
│       ├── testbed_world.yaml
│       └── testbed_world.pgm
│
├── testbed_description/
│   ├── CMakeLists.txt
│   ├── package.xml
│   └── urdf/
│
├── testbed_gazebo/
│   ├── CMakeLists.txt
│   ├── package.xml
│   └── launch/
│
└── testbed_navigation/
    ├── CMakeLists.txt
    ├── package.xml
    │
    ├── config/
    │   ├── amcl_params.yaml
    │   └── nav2_params.yaml
    │
    └── launch/
        ├── map_loader.launch.py
        ├── localization.launch.py
        └── navigation.launch.py


Name: Harsh Sengar
Contact Number: 6399166393
Email: hsrshsengar1006@gmail.com
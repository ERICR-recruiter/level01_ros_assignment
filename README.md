# Level 1: ROS2 Navigation Assignment - Sidharth Sanjay Suryawanshi

## Overview
This repository contains the completed submission for the ERIC Robotics Level 1 ROS 2 Navigation Assignment. In accordance with the project requirements, the navigation stack was built modularly using individual Nav2 plugins (`map_server`, `amcl`, planners, and behavior trees) rather than a turnkey `nav2_bringup` call. Furthermore, the environment was adapted from Gazebo Classic/Humble to **Gazebo Harmonic / ROS 2 Jazzy** on Ubuntu 24.04.

---

## Repository Structure & Deliverables
ros_nav2_assignment/
├── BUGS_FIXED.txt             # Bug-fix documentation (Root Directory)
├── README.md                  # Project submission documentation
├── testbed_description/       # Robot URDF, meshes, and RViz configs
├── testbed_gazebo/            # Harmonic worlds and spawn scripts
├── testbed_bringup/           # System bringup and maps (testbed_world.yaml)
└── testbed_navigation/        # Custom manual navigation package
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
└── config/
└── nav2_params.yaml
---

## Implementation Details & Approach

### 1. Starter Code Bug Fixes (`BUGS_FIXED.txt`)
Per assignment instructions, all intentional bugs in the starter repository were identified and resolved, and the documentation is recorded in the root directory under `BUGS_FIXED.txt`:
- **CMake Parsing & Dependencies:** Cleaned up missing configuration targets and aligned build dependencies.
- **Simulator Version Migration:** Updated launcher scripts from deprecated `gazebo_ros` (Gazebo Classic) packages to `ros_gz_sim` (Gazebo Harmonic) to support Ubuntu 24.04 / ROS 2 Jazzy.
- **Transform Tree Stabilization:** Adjusted wheel joint types to fixed configurations to clear transform tree visualization lookup errors in RViz.

### 2. Modular Navigation Package (`testbed_navigation`)
Built from scratch using `ros2 pkg create`, featuring individual launch files for full modular control:
- **Map Server (`map_loader.launch.py`):** Manages the map lifecycle using `testbed_bringup/maps/testbed_world.yaml`.
- **Localization (`localization.launch.py`):** Configures and initializes the AMCL particle filter plugin.
- **Navigation (`navigation.launch.py`):** Deploys global/local planners, costmaps, and behavior tree navigators via `nav2_params.yaml`.

---

## How to Run the Modular Navigation Stack
Open **4 separate terminals**, source your workspace in each, and run the following commands sequentially:

1. **Terminal 1 (Simulation & Bringup):**
   ```bash
   ros2 launch testbed_bringup testbed_full_bringup.launch.py
2. **Terminal 2 (Map Server):**
   ```bash
   ros2 launch testbed_navigation map_loader.launch.py
3. **Terminal 3 (AMCL Localization):**
   ```bash
   ros2 launch testbed_navigation localization.launch.py
4. **Terminal 4 (Nav2 Navigation Stack):
   ```bash
   ros2 launch testbed_navigation navigation.launch.py

## Contact Info 
 - Name: Sidharth Sanjay Suryawanshi.
 - Contact number: 9699917896
 - Email Address: sidharthsuryawanshi5634@gmail.com
Submitted by Sidharth

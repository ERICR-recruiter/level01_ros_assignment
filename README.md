# ros_assignment_ericr


# ROS 2 Navigation Assignment – Testbed T1.0.0

## Project Overview

This repository contains my implementation and investigation of the ROS 2 Navigation Assignment provided by ERIC Robotics.

The objective is to understand the robot simulation environment, investigate the provided ROS 2 packages, identify and resolve starter-code issues, and develop a modular navigation system using individual Nav2 components.

## Development Environment

| Component | Version |
|---|---|
| Operating System | Ubuntu 22.04 |
| ROS 2 | Humble|
| Build System | Colcon |
| Robot Simulator | Gazebo |
| Visualization | RViz2 |
| Programming | Python |

## Repository Structure

```text
ros_nav2_assignment_ws/
├── documentation/
│   └── tf_tree/
├── src/
│   ├── testbed_bringup/
│   ├── testbed_controller/
│   ├── testbed_description/
│   └── testbed_gazebo/
├── BUGS_AND_DEBUGGING.md
├── README.md
└── .gitignore
```

## Existing ROS 2 Packages

### 1. testbed_description
Contains the robot description, URDF/Xacro files, meshes, RViz configurations and launch files.

### 2. testbed_gazebo
Contains Gazebo simulation worlds, robot models and simulation launch files.

### 3. testbed_controller
Contains controller configurations and velocity multiplexer configurations.

### 4. testbed_bringup
Contains the complete robot bringup launch file and predefined environment maps.

## Work Completed – Initial Investigation

- Inspected the provided ROS 2 package structure.
- Investigated the robot description and launch files.
- Identified and corrected two starter-code issues.
- Launched and inspected the robot visualization environment.
- Examined joint-state information using `/joint_states`.
- Investigated the robot TF tree.
- Saved TF tree visualizations for documentation.
- Inspected simulation and controller configurations.

## Debugging Documentation

See [BUGS_AND_DEBUGGING.md](BUGS_AND_DEBUGGING.md) for identified source-code issues and runtime observations.

TF tree investigation files are available under `documentation/tf_tree/`.

## Current Development Status

| Component | Status |
|---|---|
| Starter package investigation | Completed |
| Robot description inspection | Completed |
| Initial debugging | Completed |
| TF and joint-state investigation | In progress |
| Map server implementation | Pending |
| AMCL localization | Pending |
| Nav2 planner and behavior tree setup | Pending |
| Navigation testing | Pending |

## Build Instructions

Install and source the ROS 2 environment:

```bash
source /opt/ros/humble/setup.bash
```

Build the workspace:

```bash
cd ~/ros_nav2_assignment_ws
colcon build
```

Source the workspace:

```bash
source install/setup.bash
```

## Development Objective

The next development phase is to create a new ROS 2 package named `testbed_navigation` and implement the navigation workflow using individual Nav2 components, including:

- Map Server
- AMCL
- Planner Server
- Controller Server
- Behavior Tree Navigator

The implementation will be tested incrementally in the provided simulation environment.

## Author

**Saivenkat**

GitHub: [svenkat934-byte](https://github.com/svenkat934-byte)
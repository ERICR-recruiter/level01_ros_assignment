 ## ROS 2 AMR Simulation and Navigation

## Project Overview

This project implements a simulated Autonomous Mobile Robot (AMR) using ROS 2 Humble, Gazebo Classic, RViz2, and Nav2.

The robot supports simulation, localization using AMCL, and autonomous navigation to goal positions.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic 11
- RViz2
- Nav2


## Repository Structure

- `testbed_description/` – Robot URDF and sensor descriptions
- `testbed_gazebo/` – Gazebo world and simulation resources
- `testbed_bringup/` – Robot simulation bringup
- `testbed_navigation/` – Localization and Nav2 configuration
- `start.sh` – Starts simulation, localization, and navigation

## Build Instructions

Clone the repository into the assignment workspace:

```bash
mkdir -p ~/assignment/src
cd ~/assignment/src
git clone -b freeze/level1-working-v1 https://github.com/VARAD-STACK/level01_ros_assignment_submission.git level01_ros_assignment
```

Build the workspace:

```bash
cd ~/assignment
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

## Run the Project

```bash
cd ~/assignment/src/level01_ros_assignment
chmod +x start.sh
./start.sh
```

The startup script launches the AMR simulation, localization, and Nav2 navigation.

## Navigation Documentation

For detailed launch instructions, configuration details, topics, TF frames, and debugging information, refer to:

`testbed_navigation/README.md`


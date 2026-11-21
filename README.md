# Level 1: ROS2 Navigation Assignment - Gautham P Sankar

## Overview

This repository contains a modular ROS 2 Humble navigation implementation for the **Testbed-T1.0.0** differential-drive robot. Rather than using the monolithic `nav2_bringup` stack, the `testbed_navigation` package manually configures and launches individual Nav2 lifecycle nodes for map loading, AMCL localization, and autonomous navigation.

All intentional starter-code bugs identified during setup and testing—along with their fixes—are documented in [`Bugs_and_Fixes.txt`](Bugs_and_Fixes.txt).

## Repository Structure

```text
ros_nav2_assignment/
├── testbed_bringup/
│   ├── launch/             # Launch file for bringing up the robot
│   └── maps/               # Predefined map of the test environment
├── testbed_description/
│   ├── launch/             # Launch the full base simulation
│   ├── meshes/             # 3D STL meshes for Testbed-T1.0.0
│   ├── rviz/               # RViz2 configuration files (updated with Nav2 displays)
│   └── urdf/               # URDF and Gazebo plugin files for Testbed-T1.0.0
├── testbed_gazebo/
│   ├── launch/             # Launch files for Gazebo
│   ├── models/             # Gazebo model files
│   └── worlds/             # Simulation world files
├── testbed_navigation/
│   ├── config/             # AMCL and custom Nav2 parameter files
│   ├── launch/             # Modular launch files (map loading, localization, navigation)
│   └── README.md           # Detailed navigation package documentation
├── Bugs_and_Fixes.txt      # Starter code bugs identified and resolved
├── help.md                 # Guidelines and FAQs
└── README.md               # Project overview and run instructions
```

## Requirements

- **OS:** Ubuntu 22.04
- **ROS 2:** Humble Hawksbill ([Installation Guide](https://docs.ros.org/en/humble/Installation.html))
- **Simulators:** Gazebo 11.10.2 and RViz2
- **Navigation Stack:** Nav2 (`ros-humble-navigation2`, `ros-humble-nav2-bringup`)

## Setup & Usage

### 1. Setting Up the Workspace
1. Create your workspace:
   ```bash
   mkdir -p ~/assignment_ws/src
   ```
2. Clone the repository:
   ```bash
   cd ~/assignment_ws/src
   git clone <your-fork-url>
   ```
3. Build and source the workspace:
   ```bash
   cd ~/assignment_ws/
   colcon build
   source install/setup.bash
   ```

*(Remember to run `source ~/assignment_ws/install/setup.bash` in each new terminal below.)*

### 2. Launching the Simulation Environment
**Terminal 1:**
```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
This launches the Testbed-T1.0.0 robot in Gazebo and opens RViz2 with the `map` fixed frame and Nav2 visualization displays pre-configured.

### 3. Map Loading
**Terminal 2:**
```bash
ros2 launch testbed_navigation map_loader.launch.py
```
This starts `nav2_map_server` and its dedicated lifecycle manager, dynamically resolving and publishing `testbed_bringup/maps/testbed_world.yaml` to the `/map` topic.

### 4. Localization
**Terminal 3:**
```bash
ros2 launch testbed_navigation localization.launch.py
```
This launches `nav2_amcl` with `testbed_navigation/config/amcl_params.yaml` and activates it via its own lifecycle manager to estimate the robot's pose (`map` → `odom` transform) using 2D LiDAR scans.

### 5. Navigation
**Terminal 4:**
```bash
ros2 launch testbed_navigation navigation.launch.py
```
This starts the core Nav2 navigation servers (`controller_server`, `smoother_server`, `planner_server`, `behavior_server`, `bt_navigator`, `waypoint_follower`, and `velocity_smoother`) using the customized `testbed_navigation/config/nav2_params.yaml` and activates them via `lifecycle_manager_navigation`.

### 6. Setting Initial Pose & Sending Goals
**Terminal 5:**
```bash
ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 5.0, z: 0.0}, orientation: {w: 1.0}}}}"
```
This publishes the robot's initial pose to AMCL (alternatively, use the **2D Pose Estimate** tool in RViz2). Once localized, use the **Nav2 Goal** tool in RViz2 to command autonomous navigation.

## Key Customizations

- **Robot-Specific Costmaps:** Set `robot_radius: 0.28` m based on the URDF wheel/caster geometry (accounting for the CAD-origin offset in `base_link`) and tuned `inflation_radius: 0.45` m across both local and global costmaps.
- **2D LiDAR Optimization:** Replaced `voxel_layer` with `obstacle_layer` in `local_costmap` to match the robot's 2D `/scan` sensor.
- **Planner & Controller:** Enabled A\* (`use_astar: true`) in `NavfnPlanner`, set `vy_samples: 1` in `DWBLocalPlanner` for differential-drive kinematics, and tuned wheel friction (`mu`) in `testbed.gazebo` for stable traction.
- **RViz2 Setup:** Updated `full_bringup.rviz` to use `map` as the fixed frame with Nav2 costmap, footprint, and path displays enabled.

## Demo

<p align="center">
  <video src="result.webm" width="800" autoplay loop muted playsinline>
    Simulation demo
  </video>
</p>

## Contact Info

- **Name:** Gautham P Sankar
- **Contact Number:** +91 6282212096
- **Email Address:** gauthampsankar@gmail.com
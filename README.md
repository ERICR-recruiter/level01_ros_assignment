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
│   ├── launch/             # Modular launch files (map loading, localization, navigation/
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
   git clone https://github.com/GAUTHAMPSANKAR/level01_ros_assignment.git
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

## Approach

To avoid relying on the monolithic `nav2_bringup` package, the navigation stack was decomposed into three independent lifecycle-managed stages:

1. **Map Loading (`map_loader.launch.py`):** Launches `nav2_map_server` with a dedicated lifecycle manager to publish the static occupancy grid on `/map`.
2. **Localization (`localization.launch.py`):** Launches `nav2_amcl` with its own lifecycle manager, matching `/scan` data against `/map` to broadcast the `map → odom` transform.
3. **Navigation (`navigation.launch.py`):** Launches the planning, control, smoothing, behavior, and velocity-smoothing servers under `lifecycle_manager_navigation`, consuming `/map`, `/scan`, and TF to output `/cmd_vel`.

All Nav2 parameters were tuned specifically for the Testbed-T1.0.0 URDF geometry and differential-drive kinematics rather than using default TurtleBot3 values.

## Challenges Faced

* **Starter Code & Build Issues:** Initial builds and map loading failed due to a missing `ament_package()` parenthesis in `testbed_description/CMakeLists.txt`, un-installed `maps/` and `models/` directories in CMake, and a broken image path in `testbed_world.yaml`.
* **Localization Failure (Short LiDAR Range):** The default LiDAR `<max>` range was 1.5 m, which prevented AMCL from seeing enough wall features to converge. Increasing it to 15 m resolved localization drift.
* **Robot Slip & Odometry Drift:** Friction on the rigid casters (`caster_1`–`caster_4`) caused scrubbing during in-place rotation caused slip. Setting caster friction to `0` and increasing drive-wheel friction stabilized both turning and `/odom`.
* **Gazebo Classic Verbose Warnings:** Running with `verbose:=true` exposed a leftover ROS 1 plugin (`libgazebo_ros_control.so`), a stray `>` in the IMU XML, missing IMU noise parameters, an invalid `Gazebo/Silver` material, and a non-model ROS share path in `GAZEBO_MODEL_PATH`. All were cleaned up for a warning-free startup.

*(See [`Bugs_and_Fixes.txt`](Bugs_and_Fixes.txt) for the complete file-by-file breakdown.)*


## Demo

[Result.webm](https://github.com/user-attachments/assets/5fa41e91-a82d-4873-ab61-047bc4bd52aa)

https://github.com/GAUTHAMPSANKAR/level01_ros_assignment/blob/main/Result.webm

## Contact Info

- **Name:** Gautham P Sankar
- **Contact Number:** +91 6282212096
- **Email Address:** gauthampsankar@gmail.com

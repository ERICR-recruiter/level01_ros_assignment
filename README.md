# Level 1: ROS 2 Navigation Assignment – Roshini Pinninti

## 1. Overview

This project implements a modular autonomous navigation system for the ERIC Robotics Testbed-T1.0.0 robot using **ROS 2 Humble, Gazebo, RViz, and Nav2**.

The main objective was to build the navigation workflow manually using individual Nav2 components instead of relying on the complete `nav2_bringup` launch file.

The implementation is divided into three independent stages:

1. Map loading using the Nav2 Map Server.
2. Robot localization using AMCL.
3. Autonomous navigation using individual Nav2 components.

The original simulation packages were retained, and a new package named `testbed_navigation` was developed.

## 2. Technologies Used

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic
- RViz
- Navigation2 (Nav2)
- Python launch files
- YAML configuration files
- CMake and colcon

## 3. Project Structure

```text
level01_ros_assignment/
├── testbed_bringup/
│   ├── launch/
│   └── maps/
│       ├── testbed_world.yaml
│       └── testbed_world.pgm
│
├── testbed_description/
│   ├── launch/
│   ├── rviz/
│   └── urdf/
│
├── testbed_gazebo/
│   ├── launch/
│   ├── models/
│   └── worlds/
│
├── testbed_navigation/
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── config/
│   │   ├── amcl_params.yaml
│   │   └── nav2_params.yaml
│   └── launch/
│       ├── map_loader.launch.py
│       ├── localization.launch.py
│       └── navigation.launch.py
│
├── BUGS_FIXED.txt
└── README.md
```

## 4. Implementation

### 4.1 Map Loading

The `map_loader.launch.py` file starts the Nav2 Map Server and its Lifecycle Manager.

- Loads the predefined map from `testbed_bringup/maps/testbed_world.yaml`.
- Uses the installed package share directory to locate the map.
- Automatically activates the Map Server through the Lifecycle Manager.
- Publishes the map on the `/map` topic.

The map is visualized in RViz and used by the localization and navigation components.

### 4.2 Robot Localization

The `localization.launch.py` file starts:

- **AMCL (Adaptive Monte Carlo Localization):** Estimates the robot's position on the map using LiDAR scan data and odometry.
- **Lifecycle Manager:** Automatically manages the AMCL lifecycle.

The AMCL configuration is stored in `config/amcl_params.yaml`.

Important configuration parameters:

| Parameter | Value |
|---|---|
| Global frame | `map` |
| Odometry frame | `odom` |
| Robot base frame | `base_footprint` |
| Laser scan topic | `/scan` |
| Motion model | Differential drive |
| Minimum particles | 500 |
| Maximum particles | 2000 |
| Laser maximum range | 5.0 m |

AMCL publishes localization estimates and the `map` to `odom` transform.

### 4.3 Autonomous Navigation

The `navigation.launch.py` file manually launches the required Nav2 components without using `nav2_bringup`.

The following components are used:

| Nav2 Component | Purpose |
|---|---|
| Controller Server | Computes velocity commands to follow the path |
| Planner Server | Generates a global path to the goal |
| Smoother Server | Smooths the planned path |
| Behavior Server | Executes recovery behaviors |
| BT Navigator | Coordinates the navigation task using behavior trees |
| Waypoint Follower | Supports navigation through multiple waypoints |
| Velocity Smoother | Smooths velocity commands before sending them to the robot |
| Lifecycle Manager | Manages the lifecycle of navigation nodes |

#### Planner and Controller Configuration

- **Global Planner:** NavFn (`nav2_navfn_planner/NavfnPlanner`)
- **Local Controller:** DWB (`dwb_core::DWBLocalPlanner`)
- **Path Smoother:** Simple Smoother
- **Costmaps:** Global and local costmaps
- **Obstacle Detection:** LiDAR data from `/scan`
- **Velocity Smoothing:** Velocity Smoother

The navigation parameters are configured in `config/nav2_params.yaml`.

The global costmap uses the map frame, while the local costmap uses the odometry frame with a rolling window. Both use obstacle and inflation information to support navigation and obstacle avoidance.

Velocity commands are passed through the velocity smoother before reaching the robot's `/cmd_vel` interface.

## 5. Execution Instructions

### Step 1: Build the Workspace

```bash
cd ~/assignment_ws

source /opt/ros/humble/setup.bash

colcon build

source install/setup.bash
```

### Step 2: Start the Simulation

In Terminal 1:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash

ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

This starts the robot simulation in Gazebo and RViz.

### Step 3: Load the Map

In Terminal 2:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash

ros2 launch testbed_navigation map_loader.launch.py
```

### Step 4: Start Localization

In Terminal 3:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash

ros2 launch testbed_navigation localization.launch.py
```

Set the robot's initial pose in RViz using **2D Pose Estimate** if required.

### Step 5: Start Navigation

In Terminal 4:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash

ros2 launch testbed_navigation navigation.launch.py
```

Use **Nav2 Goal** in RViz to send a navigation goal and observe the robot navigating in Gazebo.

**Note:** Run each launch command in a separate terminal and allow the previous components to initialize before starting the next stage.

## 6. Bugs Identified and Fixed

The following issues were identified and corrected in the original starter packages:

| No. | Issue | Fix |
|---|---|---|
| 1 | Incorrect map image path in the map YAML file | Corrected the image path to `testbed_world.pgm`. |
| 2 | Map directory missing from package installation | Added the `maps` directory to the installation configuration in `testbed_bringup/CMakeLists.txt`. |
| 3 | Insufficient LiDAR maximum detection range | Increased the LiDAR maximum range from 1.5 m to 5.0 m. |

Detailed information is available in [`BUGS_FIXED.txt`](BUGS_FIXED.txt).

## 7. Testing and Results

The implementation was tested in the Gazebo simulation environment and RViz.

The following functionalities were verified:

- Successful simulation startup.
- Successful map loading and `/map` publication.
- AMCL localization using LiDAR and odometry.
- Availability of the map-to-odometry transform.
- Successful activation of Nav2 navigation components.
- Global path planning in RViz.
- Autonomous robot movement towards navigation goals.
- Robot stopping after reaching the goal.

## 8. Demonstration Video

An 8-minute demonstration video is provided to show the working navigation system.

**Video Link:** https://drive.google.com/file/d/1fUR4TZkY231xV2gab0cyCEGeKEPAjfvX/view?usp=sharing

The demonstration showcases the robot simulation, map visualization, localization, navigation goal execution, and autonomous movement.

## 9. Challenges and Learning Outcomes

During implementation, the main challenges involved identifying issues in the starter packages, configuring the map and LiDAR parameters, setting up AMCL with the correct coordinate frames, and integrating individual Nav2 components.

This assignment provided practical experience with:

- ROS 2 launch system and package management.
- Nav2 plugins and lifecycle management.
- Map Server and AMCL configuration.
- Global and local costmaps.
- Path planning and velocity control.
- TF frames, LiDAR, and odometry integration.
- Modular autonomous navigation system design.

## 10. Conclusion

A modular ROS 2 navigation system was successfully implemented for the Testbed-T1.0.0 robot.

Map loading, localization, and navigation were configured using separate launch files. Individual Nav2 components were launched and managed manually, providing a better understanding of the Nav2 architecture and its plugin-based design.

The robot was successfully tested in Gazebo, demonstrating autonomous navigation towards goals provided through RViz.

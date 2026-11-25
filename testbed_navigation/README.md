# Testbed Navigation

## Overview

This package implements autonomous navigation for the Testbed T1 robot using ROS 2 Humble, Gazebo Classic, and Navigation2 (Nav2).

The Nav2 components are launched individually rather than using the complete nav2_bringup launch system.

## Package Structure

```text
testbed_navigation/
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
├── CMakeLists.txt
├── package.xml
└── README.md
```

## Components

1. Map Server: Loads the occupancy grid map.
2. AMCL: Estimates the robot's position using the map, odometry, and LiDAR.
3. Planner Server: Uses NavFn to calculate a global path.
4. Controller Server: Uses DWB to generate velocity commands.
5. Behavior Server: Provides recovery behaviors such as spinning and backing up.
6. BT Navigator: Coordinates navigation using Behavior Trees.
7. Lifecycle Managers: Configure and activate Nav2 nodes.

## Configuration

- `amcl_params.yaml`: Localization parameters and sensor settings.
- `nav2_params.yaml`: Planner, controller, costmap, behavior, and BT Navigator parameters.

Main coordinate frames:

- Global frame: `map`
- Odometry frame: `odom`
- Robot base frame: `base_footprint`
- LiDAR topic: `/scan`
- Odometry topic: `/odom`

## Build

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Running the Navigation System

Run each component in a separate Ubuntu-22.04 terminal.

### Terminal 1: Start Gazebo

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### Terminal 2: Load the map

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch testbed_navigation map_loader.launch.py
```

### Terminal 3: Start localization

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch testbed_navigation localization.launch.py
```

Use RViz's **2D Pose Estimate** tool to initialize the robot's position.

### Terminal 4: Start navigation

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```

Once all navigation components are active, use RViz's **2D Goal Pose** tool to select a destination.

## Verification

```bash
ros2 topic list
ros2 topic echo /amcl_pose --once
ros2 action list
ros2 run tf2_ros tf2_echo map base_footprint
```

The `/navigate_to_pose` action should be available when navigation is active.

## Navigation Architecture

```text
Gazebo Simulation
       |
       v
Robot Sensors and Odometry
   |              |
 /scan          /odom
   |              |
   v              v
       AMCL
        |
        v
    BT Navigator
        |
        v
   Planner Server
      (NavFn)
        |
        v
 Controller Server
      (DWB)
        |
        v
     /cmd_vel
        |
        v
   Gazebo Robot
```

## Result

The navigation system was tested in Gazebo. The robot successfully received a navigation goal through RViz, planned a path, moved autonomously, and stopped at the selected destination.

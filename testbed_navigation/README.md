
# Testbed Navigation — ROS 2 Nav2 Integration

## 1. Overview

The `testbed_navigation` package provides the navigation stack for the testbed robot using **ROS 2 Humble, Gazebo, and Nav2**.

The objective is to enable the robot to:
- Load a prebuilt occupancy-grid map.
- Estimate its position on the map using AMCL.
- Plan collision-aware paths to a goal.
- Follow planned paths using the Nav2 controller.
- Avoid obstacles detected by the LiDAR.
- Visualize the map, robot pose, costmaps, and navigation data in RViz.

The package is organized into separate launch files so that mapping, localization, navigation, and visualization can be tested independently. A combined launch file is also provided to start the complete system in sequence.

---

## 2. Package Structure

```text
testbed_navigation/
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   ├── navigation.launch.py
│   ├── rviz.launch.py
│   └── navigation_system.launch.py
├── config/
│   ├── nav2_params.yaml
│   └── amcl_params.yaml
├── README.md
├── package.xml
└── setup.py
```

**Note:** The exact contents of `config/` may differ depending on the current implementation. The map files are maintained in `testbed_bringup/maps/`, while the RViz configuration is reused from `testbed_description/rviz/full_bringup.rviz`.

### Responsibilities of the files

| File | Purpose |
|---|---|
| `map_loader.launch.py` | Starts the Nav2 map server and loads the occupancy-grid map. |
| `localization.launch.py` | Starts AMCL for estimating the robot's pose on the map. |
| `navigation.launch.py` | Starts the Nav2 navigation servers and associated lifecycle management. |
| `rviz.launch.py` | Starts RViz with the existing configuration and simulation time enabled. |
| `navigation_system.launch.py` | Orchestrates the simulation, map loading, localization, navigation, and final visualization. |
| `config/nav2_params.yaml` | Contains navigation, controller, costmap, and robot-footprint parameters. |
| `config/amcl_params.yaml` | Contains localization parameters, if maintained separately. |

---

## 3. System Architecture

The navigation pipeline follows this sequence:

```text
Gazebo Simulation
       |
       v
Robot Description and Sensors
       |
       +---- /scan
       +---- /odom
       +---- /tf
       |
       v
Map Server ------> /map
       |
       v
AMCL Localization
       |
       +---- map -> odom transform
       |
       v
Nav2 Navigation Stack
       |
       +---- Global Planner
       +---- Local Controller (DWB)
       +---- Global Costmap
       +---- Local Costmap
       +---- Behavior Server
       +---- BT Navigator
       |
       v
/cmd_vel
       |
       v
Gazebo Differential-Drive Robot

RViz visualizes the map, robot pose,
costmaps, laser scan, and planned path.
```

The simulation provides the robot's sensor and odometry data. The map server supplies the static map, AMCL estimates the robot's pose, and Nav2 uses the map and sensor data to plan and execute motion commands.

---

## 4. Map Server

The map server loads the prebuilt occupancy-grid map.

The map is stored in the `testbed_bringup` package:

```text
testbed_bringup/
└── maps/
    ├── testbed_world.pgm
    └── testbed_world.yaml
```

The YAML file describes the image, resolution, origin, and occupancy thresholds.

The current map configuration has the following characteristics:

- Resolution: `0.05 m/cell`
- Width: `405 cells`
- Height: `400 cells`
- Origin: approximately `[-10.2, -9.94, 0.0]`

The map server publishes the map on `/map`.

The map is used by AMCL for localization and by Nav2's global costmap and planner.

---

## 5. Localization with AMCL

AMCL (Adaptive Monte Carlo Localization) estimates the robot's pose in the map using the known occupancy grid and LiDAR measurements.

It uses the following key inputs and frames:

- Map topic: `/map`
- Laser scan topic: `/scan`
- Global frame: `map`
- Odometry frame: `odom`
- Robot base frame: `base_footprint`

The expected transform relationship is:

```text
map
 └── odom
      └── base_footprint
           └── base_link
                └── lidar_link_1
```

The odometry system provides the `odom -> base_footprint` transform. AMCL estimates the `map -> odom` transform.

A valid initial pose is important for reliable localization. The initial-pose parameters should correspond to the robot's actual starting position in the map. If the robot starts elsewhere, initialize its pose appropriately in RViz or update the AMCL configuration.

---

## 6. Navigation with Nav2

Nav2 provides the planning, control, obstacle avoidance, and behavior components required for autonomous navigation.

### Global planner

The global planner calculates a route from the robot's current position to the goal using the static map and global costmap.

### Local controller — DWB

The DWB controller computes velocity commands to follow the planned path while considering obstacles and trajectory costs.

### Costmaps

Nav2 uses two costmaps:

- **Global costmap:** Represents obstacles and traversable areas across the map for global planning.
- **Local costmap:** Represents nearby obstacles for local trajectory planning and obstacle avoidance.

Both costmaps should use a footprint that accurately represents the robot's physical dimensions.

---

## 7. Simulation Time and TF

Because the robot runs in Gazebo, navigation and localization nodes must use simulation time consistently.

The relevant configuration is:

```yaml
use_sim_time: true
```

The simulation publishes `/clock`. Nodes that use simulation time should obtain timestamps from this clock rather than mixing simulation timestamps with wall-clock timestamps.

The LiDAR frame must also have a valid transform to the robot base, and the transform tree must connect the robot to the `map` frame.

Known issues observed during testing include:

- LiDAR messages being dropped because the message queue is full.
- TF extrapolation errors involving timestamps earlier than the available transform data.
- Costmap transform lookups failing temporarily when requesting a transform at an unavailable time.

These are synchronization or transform-availability issues. Changing the footprint or increasing controller speed will not, by itself, resolve them.

Before tuning navigation further, verify the `/scan` timestamps, `/clock`, `use_sim_time` settings, and the availability of the required TF transforms.

---

## 8. Launching the System

### Option A — Launch the complete system

The intended one-command entry point is:

```bash
ros2 launch testbed_navigation navigation_system.launch.py
```

The orchestrator should start the following components in order:

1. Gazebo and the robot bringup.
2. Map server.
3. AMCL localization.
4. Nav2 navigation.
5. RViz visualization.

The launch delays are intended to give earlier components time to initialize before dependent components start. They do not guarantee readiness, so lifecycle states and TF availability should still be checked.

**RViz note:** If `testbed_full_bringup.launch.py` already starts RViz, disable that RViz action when using the orchestrator. Otherwise, RViz may start before navigation or appear twice.

### Option B — Launch components separately

For debugging, launch the components individually:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

In separate terminals, start the map server, localization, and navigation:

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

```bash
ros2 launch testbed_navigation localization.launch.py
```

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Launch RViz separately when required:

```bash
ros2 launch testbed_navigation rviz.launch.py
```

Use either the complete orchestrator or the separate launch sequence; do not start duplicate instances of the same nodes.

---

## 9. Build and Install

From the workspace root:

```bash
cd ~/Projects/ROS2/assignment_ws
colcon build --packages-up-to testbed_navigation
source /opt/ros/humble/setup.bash
source install/setup.bash
```

Verify the installed launch files:

```bash
ls ~/Projects/ROS2/assignment_ws/install/testbed_navigation/share/testbed_navigation/launch/
```

Verify the installed configuration files:

```bash
ls ~/Projects/ROS2/assignment_ws/install/testbed_navigation/share/testbed_navigation/config/
```

---
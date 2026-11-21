# Testbed Navigation – ROS 2 Humble

## 1. Overview

The `testbed_navigation` package implements a modular ROS 2 Navigation 2 (Nav2) workflow for the Testbed-T1.0.0 robot.

Instead of launching the complete `nav2_bringup` system, this implementation independently launches the map server, AMCL localization, planner, controller, behavior server and BT Navigator.

The package provides three separate launch files for map loading, localization and navigation.

## 2. Package Structure

```text
testbed_navigation/
├── config/
│   ├── map_server_params.yaml
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

## 3. Navigation Architecture

The navigation system consists of the following components:

### Map Server
- Package: `nav2_map_server`
- Loads the predefined `testbed_world.yaml` map.
- Publishes the map in the `map` coordinate frame.
- Uses a lifecycle manager for automatic activation.

### Localization
- Package: `nav2_amcl`
- Uses Adaptive Monte Carlo Localization (AMCL).
- Uses the differential motion model.
- Uses the likelihood field laser model.
- Publishes the robot's estimated pose in the map frame.

### Global Planner
- Plugin: `nav2_navfn_planner/NavfnPlanner`
- Calculates global paths using the global costmap.
- Uses a 0.25 m planning tolerance.

### Global Costmap
Uses three layers:
- Static Layer: incorporates the predefined map.
- Obstacle Layer: incorporates LiDAR observations from `/scan`.
- Inflation Layer: maintains clearance around obstacles.

### Local Costmap
- Uses a rolling 4 m × 4 m window.
- Updates at 5 Hz.
- Uses LiDAR observations for obstacle detection and clearing.
- Includes an inflation layer.

### Controller
- Plugin: `nav2_regulated_pure_pursuit_controller/RegulatedPurePursuitController`
- Controls the robot along the generated path.
- Supports rotation to heading.
- Uses regulated linear velocity scaling.
- Enables collision detection.

### Behavior Server
Implements the following recovery behaviours:
- Spin
- BackUp
- Wait

### BT Navigator
- Package: `nav2_bt_navigator`
- Coordinates navigation actions.
- Uses Nav2's default behaviour tree configuration.
- Loads the required Nav2 behaviour-tree plugins.

## 4. Configuration Files

| File | Purpose |
|---|---|
| `map_server_params.yaml` | Map server configuration |
| `amcl_params.yaml` | Localization parameters |
| `nav2_params.yaml` | Planner, controller, costmap, behavior and BT Navigator parameters |

Important coordinate frames:

- Global frame: `map`
- Odometry frame: `odom`
- Robot base frame: `base_footprint`

Simulation time is enabled for the navigation components.

## 5. Building the Workspace

Source ROS 2 Humble:

```bash
source /opt/ros/humble/setup.bash
```

Build the workspace:

```bash
cd ~/assignment_ws/
colcon build --symlink-install
```

Source the workspace:

```bash
source install/setup.bash
```

## 6. Running the Navigation System

Start the components in separate terminals.

### Terminal 1 – Robot Simulation

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### Terminal 2 – Map Server

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

### Terminal 3 – Localization

```bash
ros2 launch testbed_navigation localization.launch.py
```

### Terminal 4 – Navigation

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Keep all terminals running while testing.

## 7. RViz Setup and Navigation

1. Open RViz using the configuration provided by the simulation.
2. Set the Fixed Frame to `map`.
3. Verify that the map is displayed.
4. Use the `2D Pose Estimate` tool to initialize the robot's estimated position when required.
5. Use the `Nav2 Goal` tool to select a navigation destination.
6. Observe the generated global path and robot movement.

## 8. Testing and Verification

The implementation was tested in the Gazebo simulation environment.

The following behaviours were verified:

- Map loading and publication.
- AMCL localization.
- Global path planning.
- Autonomous navigation to selected goals.
- Global and local costmap visualization.
- Dynamic obstacle detection using LiDAR.
- Path replanning around an inserted obstacle.
- Collision prevention.
- Navigation recovery behaviour testing.

## 9. Dependencies

The package requires:

- ROS 2 Humble
- Gazebo Classic
- Nav2
- `nav2_map_server`
- `nav2_amcl`
- `nav2_planner`
- `nav2_navfn_planner`
- `nav2_controller`
- `nav2_regulated_pure_pursuit_controller`
- `nav2_costmap_2d`
- `nav2_behaviors`
- `nav2_bt_navigator`
- `nav2_behavior_tree`
- `nav2_lifecycle_manager`

## 10. Conclusion

The `testbed_navigation` package provides a modular implementation of the ROS 2 Nav2 navigation workflow.

By independently launching the map server, localization and navigation components, the implementation demonstrates how Nav2 plugins can be configured and managed without relying on the complete `nav2_bringup` launch system.

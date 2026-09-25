# Level 1: ROS2 Navigation Assignment - Saket Umesh Sagar

## 1. Objective

The objective of this assignment is to develop a modular ROS 2 navigation package, \`testbed_navigation\`, for the ERIC Robotics Testbed-T1.0.0 robot.

The navigation stack is implemented by manually assembling the required Nav2 components rather than using the monolithic \`nav2_bringup\` package. This provides independent launch and configuration of the map server, localization, planning, control, behavior tree navigation, and lifecycle management components.

The implementation focuses on:

\- Loading and publishing the provided occupancy-grid map.

\- Localizing the robot within the map using AMCL.

\- Configuring global and local costmaps using the available robot sensors.

\- Integrating a global planner and local controller through Nav2's plugin architecture.

\- Configuring the Behavior Tree Navigator and navigation behaviors.

\- Managing Nav2 lifecycle nodes independently.

\- Validating the complete navigation pipeline through simulation.

\- Documenting the debugging, configuration, and testing process.

Only basic autonomous navigation functionality is required for the assignment. Therefore, the implementation initially uses established Nav2 plugins and subsequently evaluates alternative planner plugins while keeping the remainder of the navigation stack unchanged.

---

## 2. Navigation Architecture

The navigation system is organized as a set of independent ROS 2/Nav2 components rather than being launched through \`nav2_bringup\`.

The overall navigation workflow is:

\`\`\`text

                    testbed_world.yaml

                           │

                           ▼

                     ┌───────────┐

                     │ Map Server│

                     └─────┬─────┘

                           │

                          /map

                           │

                           ▼

                     ┌───────────┐

                     │    AMCL   │

                     └─────┬─────┘

                           │

                      map → odom

                           │

                           ▼

                    ┌──────────────┐

                    │ Global       │

                    │ Costmap      │

                    │              │

                    │ Static Layer │

                    │ Inflation    │

                    └──────┬───────┘

                           │

                           ▼

                    ┌──────────────┐

                    │Planner Server│

                    │              │

                    │ NavFn        │

                    └──────┬───────┘

                           │

                       Global Path

                           │

                           ▼

                    ┌──────────────┐

                    │ Local        │

                    │ Costmap      │

                    │              │

                    │ Obstacle     │

                    │ Inflation    │

                    └──────┬───────┘

                           │

                           ▼

                    ┌──────────────┐

                    │ Controller   │

                    │ Server       │

                    │              │

                    │ DWB          │

                    └──────┬───────┘

                           │

                       /cmd_vel

                           │

                           ▼

                    ┌──────────────┐

                    │ Diff Drive   │

                    │ Controller   │

                    └──────┬───────┘

                           │

                           ▼

                         Robot

\`\`\`

The Behavior Tree Navigator provides the high-level navigation workflow and coordinates the planning, control, and recovery components.

The major components are separated into the following launch stages:

### 2.1 Map Loading

\`map_loader.launch.py\` launches:

\* \`nav2_map_server\`

\* Nav2 lifecycle manager

The map server loads the occupancy-grid YAML configuration provided by the \`testbed_bringup\` package and publishes the \`/map\` topic.

### 2.2 Localization

\`localization.launch.py\` is responsible for:

\* AMCL-based localization.

\* Maintaining the \`map → odom\` transform.

\* Managing the localization node's lifecycle.

### 2.3 Navigation

\`navigation.launch.py\` will bring together:

\* Global costmap.

\* Local costmap.

\* Planner server.

\* Controller server.

\* Behavior Tree Navigator.

\* Behavior server.

\* Navigation lifecycle manager.

The initial navigation implementation will use **\*\*NavFn\*\*** as the global planner and **\*\*DWB\*\*** as the local controller. Alternative planner plugins such as **\*\*Smac 2D\*\*** and **\*\*Theta\*\***\* will subsequently be tested while keeping the rest of the navigation stack unchanged.

This allows planner behavior to be evaluated independently without changing the overall navigation architecture.

## 3. Starter Code Investigation

I first tried building and running the provided starter workspace.

\- Ran \`colcon build\` → build failed with a CMake parse error.

\- Investigated the error and found that \`ament_package\` was written without \`()\`. Fixed it to \`ament_package()\`.

\- Rebuilt the workspace → build progressed further.

\- While checking the launch files, found a missing space between the Xacro executable and the \`.xacro\` file path in \`robot_description.launch.py\`. Added the missing \`" "\` separator.

\- While checking the map configuration, found that \`testbed_world.yaml\` referenced \`wrong_path_testbed_world.pgm\`, which did not exist. Corrected it to \`testbed_world.pgm\`.

\- Started testing the map using Nav2's \`map_server\`. The map server failed to load the YAML file from the installed package.

\- Investigated the installed package and found that the \`maps/\` directory was not being installed by \`testbed_bringup/CMakeLists.txt\`.

\- Updated the CMake install rule of testbed_description to install both \`launch\` and \`maps\`.

\- Rebuilt \`testbed_bringup\` after updating its CMake install rule and relaunched \`map_loader.launch.py\`.

\- \`map_server\` successfully found and loaded both \`testbed_world.yaml\` and \`testbed_world.pgm\`, then transitioned to the active state.

\- Verified that \`/map\` publishes a \`nav_msgs/msg/OccupancyGrid\`.

\- Added \`/map\` to RViz and confirmed that the map is rendered correctly.

\- Launched AMCL and initially observed \`Waiting for map...\` until the map became available.

\- AMCL successfully received the 405 × 400 occupancy map and created the laser model.

\- Since no initial pose was configured, AMCL requested an initial pose.

\- Published the initial pose through \`/initialpose\` from the terminal instead of using RViz.

\- Verified that AMCL began publishing \`/amcl_pose\` and the \`map -> odom\` transform.

During runtime testing:

\- Gazebo's \`gzclient\` crashed with a rendering assertion while \`gzserver\` and the ROS nodes continued running.

\- Tested the system in headless mode and launched the Gazebo GUI separately.

\- RViz showed LiDAR message-filter warnings, so I checked the TF tree, transforms, \`/clock\`, \`/scan\`, and \`use_sim_time\` configuration.

\- Identified that \`robot_state_publisher\` was using \`use_sim_time: false\` while other simulation-related nodes were using simulation time. Changed it to \`true\` to resolve the timing inconsistency. However, the LiDAR message-filter warnings persisted.

\- Verified that the required TF chain was present. The cause of the remaining LiDAR warnings was not established, so no further unverified modifications were made.

\- Encountered an unresponsive ROS 2 CLI daemon, which caused \`ros2 node list\` and \`ros2 action list\` to hang even though the nodes were visible in \`rqt_graph\`.

\- Verified that \`ros2 node list --no-daemon\` successfully listed the active nodes.

\- Identified the stuck daemon process (PID \`13457\`), terminated it, and restarted the daemon.

\- Verified that \`ros2 node list\` and \`ros2 action list\` subsequently worked correctly, displaying the active nodes and planner path-computation actions.

### Nav2 Planner Integration and Runtime Validation

\- Created the custom Nav2 configuration for the planner server in \`testbed_navigation/config/nav2_params.yaml\`.

\- Configured the global costmap with the \`static_layer\` and \`inflation_layer\` plugins.

\- Selected \`nav2_navfn_planner/NavfnPlanner\` as the initial global planner.

\- Configured the planner server to use the global costmap and the \`GridBased\` planner plugin.

\- Verified that the global costmap was created under \`/global_costmap/global_costmap\` and that its configured plugins were loaded.

\- Created and tested \`navigation.launch.py\` to launch the planner server with its lifecycle manager.

\- Observed a lifecycle bond connection timeout during planner activation. Increased the lifecycle manager's \`bond_timeout\` parameter and relaunched the navigation component.

\- Verified that the planner server successfully established a bond with its lifecycle manager and transitioned to the active state.

\- Confirmed that the planner server was visible in the ROS 2 node graph alongside AMCL, the map server, and the lifecycle managers.

### ROS 2 CLI and Action Server Validation

\- Observed that \`ros2 node list\` and \`ros2 action list\` were hanging despite the nodes being visible in \`rqt_graph\`.

\- Verified that \`ros2 node list --no-daemon\` successfully listed the active ROS 2 nodes.

\- Identified a stuck ROS 2 CLI daemon process running with ROS domain ID \`7\` and CycloneDDS.

\- Terminated the stuck daemon process and restarted the ROS 2 CLI daemon.

\- Verified that \`ros2 node list\` and \`ros2 action list\` subsequently worked as expected.

\- Confirmed that the planner server advertised the following path-computation actions:

  \- \`/compute_path_to_pose\`

  \- \`/compute_path_through_poses\`

### Navigation Stack Integration and Validation

- Integrated the main Nav2 components manually, without using `nav2_bringup`.
- Configured the localization lifecycle manager for `map_server` and AMCL, and the navigation lifecycle manager for the planner, controller, and Behavior Tree navigation components.
- Configured **NavFn** (`nav2_navfn_planner/NavfnPlanner`) as the global planner and **DWB** as the local controller.
- Confirmed that the navigation nodes transitioned to the active state after adjusting the lifecycle manager's `bond_timeout` to `10.0`.
- Confirmed that the `/navigate_to_pose` and `/compute_path_to_pose` actions are available.
- Verified that the robot publishes `/odom`, the map server publishes `/map`, and AMCL publishes `/amcl_pose` and the `map → odom` transform.
- Verified the TF chain: `map → odom → base_footprint → base_link → lidar_link_1`.

### Localization and Sensor Issues

- During rotation/localization tests, the `map → odom` transform showed large changes, while a separate check of the `odom → base_footprint` yaw was comparatively smooth.
- AMCL pose estimates varied substantially and showed high covariance in the observed samples. These observations suggest localization instability, but the root cause has not been established.
- RViz continued to report LiDAR message-filter warnings for `lidar_link_1` indicating that message timestamps were earlier than the available transform cache. Costmap logs also reported that the robot was out of bounds.
- The cause of these issues remains unresolved. No unverified root cause or fix is claimed.

### Current Navigation Status

- The Nav2 stack is integrated and active, including the map server, AMCL, costmaps, planner, controller, and Behavior Tree Navigator.
- The `/navigate_to_pose` action is available and accepts navigation goals.
- **Goal execution is not reliable:** the robot does not successfully navigate to the requested goal. During testing, instability in the `map → odom` transform causes the navigation system to behave as though the goal has been reached even though the robot has not physically reached it.
- This apparent success is a false goal-completion result, not successful autonomous navigation.
- Localization instability, LiDAR transform-timing warnings, and costmap out-of-bounds warnings remain unresolved.

### Remaining Work

- Investigate the AMCL pose and `map → odom` instability, which appears to be associated with the false goal-completion behavior observed during testing.
- Resolve or isolate the LiDAR message-filter and costmap out-of-bounds warnings.
- Correct the goal-completion behavior and validate that the robot physically reaches its target before reporting success.
- Record the final test conditions and results after reliable goal execution is demonstrated.

---

## 3. Raw Logs and Recorded Output

This section preserves selected runtime output and measurements recorded during debugging. These are excerpts, not a complete terminal capture; outputs are included only where they were recorded.

### 3.1 TF Message-Filter Warning

```text
Message Filter dropping message: frame 'lidar_link_1' ... timestamp on message is earlier than all data in the transform cache
```

### 3.2 Costmap Warning

```text
Robot is out of bounds
```

### 3.3 `map → odom` Transform Samples

Recorded `tf2_echo map odom` samples:

```text
Time ~477–483 s:
  Translation: [0.143, 0.594]
  Yaw:          1.386°

Time ~484 s:
  Translation: [0.522, -0.214]
  Yaw:          5.499°

Time ~489 s:
  Translation: [1.176, -0.952]
  Yaw:         10.756°

Time ~492 s:
  Translation: [-1.330, 4.460]
  Yaw:        -53.679°
```

### 3.4 AMCL Pose Observations

- The recorded AMCL pose samples varied substantially during the same test, with position estimates shifting from approximately `(9.3, 5.0)` to `(7.7, -0.25)`.
- The observed position covariance values exceeded `4` in the captured samples; yaw covariance was approximately `2`.
- These are selected observations, not a complete `/amcl_pose` message dump.

### 3.5 Runtime Validation Notes

```text
/navigate_to_pose       — action available; accepts goals
/compute_path_to_pose   — action available
/map                    — OccupancyGrid published
/odom                   — odometry published
/amcl_pose              — AMCL pose published
```

**Note:** The goal-acceptance/action availability checks passed, but physical goal arrival was not validated. During testing, the system sometimes reported goal completion even though the robot had not physically reached the target. The association with `map → odom` instability is an observed debugging hypothesis, not a confirmed root cause.

---

## 4. Navigation Architecture

The navigation stack is assembled from independently launched Nav2 components rather than `nav2_bringup`.

| Component | Responsibility |
|---|---|
| Map Server | Loads the occupancy-grid map and publishes `/map`. |
| AMCL | Estimates the robot pose and provides the `map → odom` transform. |
| Global Costmap | Represents the map and applies configured costmap layers. |
| Planner Server | Computes a global path using NavFn (`nav2_navfn_planner/NavfnPlanner`). |
| Local Costmap | Provides local obstacle and inflation information for control. |
| Controller Server | Uses DWB to generate velocity commands along the path. |
| Behavior Tree Navigator | Coordinates the goal-based navigation workflow. |
| Lifecycle Managers | Manage the lifecycle of localization and navigation nodes. |

The configured navigation stack is active and accepts goals through `/navigate_to_pose`. However, reliable physical arrival at the goal has not been demonstrated. During testing, the system sometimes reported goal completion before the robot reached the target; this was observed alongside instability in `map → odom`, but the root cause is not confirmed.

## 5. Package Structure

The assignment workspace contains the following packages:

```text
ERIC_Robotics_Assignment/
├── testbed_description/
├── testbed_gazebo/
├── testbed_bringup/
└── testbed_navigation/
    ├── config/
    │   └── nav2_params.yaml
    └── launch/
        ├── map_loader.launch.py
        ├── localization.launch.py
        └── navigation.launch.py
```

This is a high-level view of the packages and files referenced in the development notes. Other files may exist in the workspace.

## 6. System Setup and Dependencies

### Environment

- ROS 2 Humble
- Gazebo Classic 11
- Nav2 components used by the manually assembled stack
- `colcon` for building the workspace

### Build and source

Run from the workspace root:

```bash
cd ~/assignment_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

If the workspace has already been built, source the ROS 2 and workspace setup files in each new terminal before running ROS commands.

## 7. Launch and Execution Guide

The launch files are separated by responsibility. Start the simulation and robot using the bringup packages, then start map loading, localization, and navigation.

### 7.1 Launch the simulation

Launch the Testbed Gazebo world and robot using the launch file provided by `testbed_gazebo` / `testbed_bringup`. The exact launch command depends on the launch file available in the workspace.

### 7.2 Load the map

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

This starts the map server and its lifecycle manager. Verify that `/map` is being published.

### 7.3 Start localization

```bash
ros2 launch testbed_navigation localization.launch.py
```

Provide an initial pose through `/initialpose` when requested, then verify `/amcl_pose` and the `map → odom` transform.

### 7.4 Start navigation

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Verify that the Nav2 nodes are active and that `/navigate_to_pose` is available. Goals may be sent through the action interface or RViz. **Action availability and goal acceptance do not establish successful navigation**; confirm that the robot physically reaches the target.

---


## Contact Info 
 - Name: Saket Umesh Sagar
 - Contact number: 7972273560
 - Email Address: saketsagar22@gmail.com
---

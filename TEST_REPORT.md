# Test and Verification Report
## ERIC Robotics — Level 1 ROS 2 Navigation Assignment

### 1. Execution Environment

| Attribute | Verified Environment |
|---|---|
| Operating System | Ubuntu 22.04 LTS |
| ROS 2 Distribution | Humble Hawksbill |
| Simulator | Gazebo Classic 11.10.2 |
| Navigation Framework | Nav2 |
| Visualization | RViz2 |
| Middleware | Cyclone DDS |
| Robot | Testbed-T1.0.0 differential-drive robot |

### 2. Static and Configuration Verification

The project includes the following verification work:

- URDF/Xacro robot-description validation.
- SDF and Gazebo world validation.
- Robot link and joint structure inspection.
- STL mesh geometry inspection.
- Gazebo plugin configuration inspection.
- YAML configuration parsing.
- Nav2 parameter and lifecycle configuration inspection.
- Python launch-file syntax validation.
- Map file and map YAML validation.

The repository's original static verification report records 98/98 checks passed.

### 3. Live Runtime Verification

All runtime tests below were performed on Ubuntu 22.04 with ROS 2 Humble and Gazebo Classic.

| No. | Runtime Test | Result | Evidence |
|---|---|---|---|
| 1 | Workspace build and package launchability | PASS | Navigation packages launched successfully |
| 2 | Gazebo world startup | PASS | Gazebo Classic world opened |
| 3 | Robot description and TF publication | PASS | Robot links published by robot_state_publisher |
| 4 | Robot spawning | PASS | SpawnEntity reported successful spawning of testbed |
| 5 | Differential-drive odometry | PASS | /odom published by diff_drive_control |
| 6 | Velocity command interface | PASS | /cmd_vel connected to diff_drive_control |
| 7 | LiDAR visualization | PASS | /scan data visible in RViz |
| 8 | Map server lifecycle | PASS | /map_server reported active [3] |
| 9 | AMCL localization lifecycle | PASS | /amcl reported active [3] |
| 10 | Initial pose estimation | PASS | /amcl_pose published and map-to-base_footprint TF verified |
| 11 | Nav2 planner lifecycle | PASS | /planner_server reported active [3] |
| 12 | Nav2 controller lifecycle | PASS | /controller_server reported active [3] |
| 13 | Nav2 smoother lifecycle | PASS | /smoother_server reported active [3] |
| 14 | Nav2 behavior server lifecycle | PASS | /behavior_server reported active [3] |
| 15 | BT navigator lifecycle | PASS | /bt_navigator reported active [3] |
| 16 | Autonomous goal execution | PASS | Robot travelled to the selected goal and stopped |
| 17 | Gazebo and RViz motion correspondence | PASS | Robot motion observed in both applications |

### 4. Navigation Architecture

The navigation system uses the following transform structure:

map -> odom -> base_footprint -> base_link

The robot description publishes the static robot-link transforms. The differential-drive plugin provides odometry and the odom-to-base_footprint transform. AMCL provides map-to-odom localization.

The Nav2 stack includes:

- Map Server
- AMCL localization
- Planner Server using NavFn
- Controller Server using Regulated Pure Pursuit
- Smoother Server
- Behavior Server
- BT Navigator
- Lifecycle Manager

The global and local costmaps use the robot's LiDAR data for obstacle information.

### 5. Autonomous Navigation Demonstration

The following live behaviour was demonstrated:

1. Gazebo Classic started with the Testbed world.
2. The Testbed robot was spawned successfully.
3. The occupancy-grid map was loaded.
4. AMCL localization was activated.
5. All seven lifecycle-managed navigation components became active.
6. A navigation goal was selected in RViz.
7. Nav2 generated a path and issued velocity commands.
8. The robot moved in Gazebo while its corresponding motion was visualized in RViz.
9. The robot reached the selected destination and stopped.

A screen recording of approximately 52 seconds was captured as demonstration evidence.

### 6. Known Issues and Workarounds

- The combined testbed_full_bringup launch caused Gazebo server crashes on the tested machine. The modular launch sequence was used successfully instead.
- Gazebo Classic displays an end-of-life warning. This is a simulator lifecycle notice.
- AMCL requires a valid initial pose before it can publish a reliable localization transform.
- All ROS 2 nodes must use simulation time when operating with the Gazebo clock.
- Cyclone DDS was used consistently across terminals to maintain ROS 2 communication.

### 7. Evidence to Include with Submission

Recommended evidence files:

- Gazebo simulation screenshot.
- RViz map and LiDAR screenshot.
- RViz localization screenshot.
- RViz planned navigation path screenshot.
- Gazebo and RViz navigation demonstration video.

### 8. Final Result

The modular ROS 2 navigation system was successfully launched and tested on Ubuntu 22.04, ROS 2 Humble and Gazebo Classic 11.10.2.

The robot was spawned, localized using AMCL, controlled through Nav2, and successfully navigated to a selected goal.

**Overall runtime navigation demonstration: SUCCESSFUL.**

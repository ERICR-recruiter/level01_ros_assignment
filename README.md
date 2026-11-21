# Level 1: ROS 2 Navigation Assignment - Natasha N Bhandari

**Candidate**: Natasha N Bhandari  
**Contact Number**: `+91 9449109766`  
**Email Address**: `nnatashabhandari@gmail.com`  
**Target Organization**: ERIC Robotics  
**Repository**: [level01_ros_assignment](file:///home/zeo/assignment_ws/src/level01_ros_assignment/)  
**Environment**: ROS 2 Humble | Gazebo Classic 11.10.2 | Ubuntu 22.04 LTS  

---

## 1. Technical Review Summary (First-Person Briefing)

> *"In this assignment, my objective was to establish a fully modular, robust ROS 2 Humble autonomous navigation stack for the ERIC Robotics Testbed-T1.0.0 differential drive robot without relying on monolithic bringup wrappers like `nav2_bringup`. 
>
> I began by auditing the starter repository, systematically verifying and resolving 8 underlying issues across CMake scripts, Gazebo models, XML definitions, launch arguments, and an obsolete ROS 1 Gazebo plugin that was crashing `gzserver` with a segmentation fault. Every fix is documented in [BUGS_IDENTIFIED.txt](file:///home/zeo/assignment_ws/src/level01_ros_assignment/BUGS_IDENTIFIED.txt).
>
> Next, I developed the [testbed_navigation](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_navigation/) package from scratch. I designed it around isolated, independently testable lifecycle stages: manual Map Loading, AMCL Localization, and 2D Autonomous Navigation. I inspected the URDF and Gazebo plugins to extract the robot's physical constraints—notably its differential drive kinematics and its $1.5\,\text{m}$ LiDAR limit—and tuned NavFn, DWB Local Planner, costmap raytracing, and recovery behaviors specifically to those hardware specifications.
>
> Finally, I validated the entire staged workflow in simulation. The robot successfully loaded the $405 \times 400$ occupancy grid, established a complete `map → odom → base_footprint` TF transform chain, converged particles upon 2D pose estimation, and navigated to a dispatch goal via the `/navigate_to_pose` action server with status `SUCCEEDED`. All genuine screenshots captured during execution are preserved in [evidence/](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/)."*

---

## 2. Robot System Specifications & Traced Architecture

All parameters and configurations were derived directly from the source packages ([testbed_description](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/), [testbed_gazebo](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_gazebo/), and [testbed_bringup](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_bringup/)):

| Attribute | Specification | Source in Repository |
| :--- | :--- | :--- |
| **Drive Kinematics** | Two-wheel Differential Drive | [testbed.gazebo](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/urdf/testbed.gazebo) (`libgazebo_ros_diff_drive.so`) |
| **Wheel Separation** | $0.35\,\text{m}$ | `wheel_separation`: `0.35` in diff drive plugin |
| **Wheel Diameter** | $0.10\,\text{m}$ (Radius: $0.05\,\text{m}$) | `wheel_diameter`: `0.1` in diff drive plugin |
| **Robot Radius** | $0.25\,\text{m}$ | Geometric bounding circle around wheels & chassis |
| **Spawn Pose** | $(x=0.0\,\text{m}, y=5.0\,\text{m}, z=0.0\,\text{m}, \text{yaw}=0.0\,\text{rad})$ | [spawn_testbed.launch.py](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_gazebo/launch/spawn_testbed.launch.py#L15) |
| **LiDAR Sensor Range** | Min: $0.10\,\text{m}$, Max: $1.50\,\text{m}$, 60 samples | [testbed.gazebo](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/urdf/testbed.gazebo) (`ray` sensor, line 78) |
| **Base / Body Frame** | `base_footprint` | [testbed.xacro](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/urdf/testbed.xacro) |
| **Odometry Frame** | `odom` | Broadcast by Gazebo diff-drive plugin |
| **Map Frame** | `map` | Broadcast by Nav2 AMCL (`map → odom`) |
| **Laser Frame** | `lidar_link_1` | Broadcast by `robot_state_publisher` |
| **Velocity Command Topic** | `/cmd_vel` (`geometry_msgs/msg/Twist`) | Subscribed by Gazebo diff-drive plugin |
| **Laser Scan Topic** | `/scan` (`sensor_msgs/msg/LaserScan`) | Published by Gazebo ray sensor plugin |
| **Odometry Topic** | `/odom` (`nav_msgs/msg/Odometry`) | Published by Gazebo diff-drive plugin |
| **Occupancy Map** | [testbed_world.yaml](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_bringup/maps/testbed_world.yaml) | $405 \times 400$ cells, $0.05\,\text{m/cell}$, origin $[-10.2, -9.94, 0.0]$ |

---

## 3. Nav2 Plugin Selection & Design Rationale

Rather than running monolithic scripts, each plugin in [nav2_params.yaml](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_navigation/config/nav2_params.yaml) was purposefully selected for Testbed-T1.0.0:

1. **Global Planner (`nav2_navfn_planner/NavfnPlanner`)**:
   - *Why*: Testbed-T1.0.0 is a planar indoor ground mobile robot. NavFn utilizes Dijkstra/A* dynamic programming over the 2D occupancy grid, calculating the shortest obstacle-free path with minimal computational overhead.
2. **Local Controller (`dwb_core::DWBLocalPlanner`)**:
   - *Why*: DWB local planner rollouts evaluate non-holonomic velocity pairs $(v_x, \omega_z)$ while enforcing $v_y = 0$. Its modular critics (`RotateToGoal`, `PathAlign`, `GoalDist`, `BaseObstacle`, `Oscillation`) allow smooth in-place rotations and precise stopping within the $0.25\,\text{m}$ goal tolerance.
3. **Obstacle & Inflation Costmap Layers**:
   - *Why*: The robot's LiDAR physical range is only $1.50\,\text{m}$. Standard Nav2 configurations assume $3.0\,\text{m}$ to $5.0\,\text{m}$ lasers. Setting `obstacle_max_range: 1.5` and `raytrace_max_range: 1.5` prevents costmap corruption caused by querying non-existent sensor rays beyond physical hardware bounds. Inflation radius is set to $0.45\,\text{m}$ with a cost scaling factor of $3.0$ to ensure the $0.25\,\text{m}$ robot maintains safe clearance from walls and fences.
4. **Recovery Behaviors (`nav2_behaviors`)**:
   - *Why*: Configured `Spin`, `BackUp`, `DriveOnHeading`, and `Wait`. Because differential drive robots can spin on their center of rotation without lateral translation, in-place spinning and straight backing-up provide the safest recovery maneuvers when navigating narrow passages.
5. **Velocity Smoother (`nav2_velocity_smoother`)**:
   - *Why*: Serves as a buffer between the local trajectory controller and the Gazebo simulation motors (`/cmd_vel_nav` $\rightarrow$ `/cmd_vel`), limiting linear acceleration to $2.5\,\text{m/s}^2$ and angular acceleration to $3.2\,\text{rad/s}^2$ to prevent wheel slip.
6. **BT Navigator (`nav2_bt_navigator`)**:
   - *Why*: Uses the standard ROS 2 Humble behavior tree `navigate_to_pose_w_replanning_and_recovery.xml` accompanied by all 48 ROS 2 Humble BT plugin libraries to handle runtime replanning and dynamic recovery cascading.

---

## 4. Verified Starter Bugs & Corrections

Before navigation could be developed, 8 issues in the starter code were identified, resolved, and verified. Details are cataloged in [BUGS_IDENTIFIED.txt](file:///home/zeo/assignment_ws/src/level01_ros_assignment/BUGS_IDENTIFIED.txt):

| # | File | Observed Bug | Fix Applied |
| :- | :--- | :--- | :--- |
| **1** | [testbed_description/CMakeLists.txt](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/CMakeLists.txt#L23) | `ament_package` lacked invocation parentheses `()` causing CMake syntax error | Added `()` to make `ament_package()` |
| **2** | [testbed_bringup/CMakeLists.txt](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_bringup/CMakeLists.txt#L14) | `maps` directory omitted from `install(DIRECTORY ...)` directive | Added `maps` directory to CMake install rule |
| **3** | [testbed_gazebo/CMakeLists.txt](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_gazebo/CMakeLists.txt#L14) | `models` directory omitted from `install(DIRECTORY ...)` directive | Added `models` directory to CMake install rule |
| **4** | [testbed_bringup/maps/testbed_world.yaml](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_bringup/maps/testbed_world.yaml#L1) | Image path referenced non-existent file `wrong_path_testbed_world.pgm` | Corrected image filename to `testbed_world.pgm` |
| **5** | [testbed_description/urdf/testbed.gazebo](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/urdf/testbed.gazebo#L40) | Malformed XML with trailing `>` on `<initial_orientation_as_reference>` tag | Removed extraneous `>` |
| **6** | [testbed_gazebo/launch/spawn_playground.launch.py](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_gazebo/launch/spawn_playground.launch.py#L45-L50) | `world` argument not forwarded to `gazebo.launch.py`, loading empty world | Forwarded `world`, `gui`, and `server` via `LaunchConfiguration` |
| **7** | [testbed_description/rviz/full_bringup.rviz](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/rviz/full_bringup.rviz#L251-L257) | Goal tool configured as `rviz_default_plugins/SetGoal` instead of Nav2 action tool | Replaced with `nav2_rviz_plugins/GoalTool`, set fixed frame `map`, added Map/AMCL displays |
| **8** | [testbed_description/urdf/testbed.gazebo](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_description/urdf/testbed.gazebo#L6-L8) | Obsolete ROS 1 plugin `libgazebo_ros_control.so` crashed `gzserver` with SIGSEGV (code -11) | Commented out plugin (motor control handled by `diff_drive`) |

---

## 5. Build and Staged Execution Guide

To reproduce the workflow on your machine, open **separate terminals** and source the workspace in each:

### Stage 1: Build Workspace
```bash
cd ~/assignment_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

### Stage 2: Launch Base Simulation & RViz
```bash
# Terminal 1
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
*Verification*: Gazebo opens showing the playground world; RViz loads showing the robot model at $(0, 5, 0)$.

### Stage 3: Map Loading
```bash
# Terminal 2
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation map_loader.launch.py use_sim_time:=true
```
*Verification*: `ros2 lifecycle get /map_server` outputs `active [3]`. The $405 \times 400$ occupancy grid appears in RViz under the `Map` display.

### Stage 4: AMCL Localization
```bash
# Terminal 3
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation localization.launch.py load_map:=false use_sim_time:=true
```
*Verification*: `ros2 lifecycle get /amcl` outputs `active [3]`.

### Stage 5: Navigation Stack
```bash
# Terminal 4
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation navigation.launch.py use_sim_time:=true
```
*Verification*: `ros2 lifecycle get /controller_server` outputs `active [3]`. Action server `/navigate_to_pose` is available.

---

## 6. How to Initialize AMCL and Send Goals in RViz

1. **Set Initial Pose**:
   - In the RViz top toolbar, click **2D Pose Estimate**.
   - Click and drag on the map at the robot's spawn position: $x = 0.0\,\text{m}$, $y = 5.0\,\text{m}$, facing along the positive X-axis ($\text{yaw} = 0.0$).
   - *CLI Alternative*:
     ```bash
     ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
     "{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 5.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.068]}}"
     ```
   - Observe the green particle cloud (`/particlecloud`) snapping around the robot's footprint and aligning with the laser scan.
2. **Send a Navigation Goal**:
   - In the RViz top toolbar, select **2D Goal Pose** (configured to `nav2_rviz_plugins/GoalTool`).
   - Click on a free space ahead of the robot (e.g., $x = 1.0\,\text{m}$, $y = 5.0\,\text{m}$) and drag the arrow to set desired heading.
   - *CLI Alternative*:
     ```bash
     ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
     "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 5.0, z: 0.0}, orientation: {w: 1.0}}}}" --feedback
     ```
   - Observe the global path line appear, the local costmap updating, and the robot driving autonomously to the target pose until status `SUCCEEDED` is returned.

---

## 7. Diagnostic & Verification Commands

| Component | Diagnostic Command | Expected Output / Check |
| :--- | :--- | :--- |
| **Topic Availability** | `ros2 topic list` | `/scan`, `/odom`, `/map`, `/amcl_pose`, `/cmd_vel` all listed |
| **Transform Chain** | `ros2 run tf2_ros tf2_echo map base_footprint` | Continuous translation & rotation output without frame drops |
| **Odometry Transform**| `ros2 run tf2_ros tf2_echo odom base_footprint` | Valid high-frequency odometry transform from Gazebo |
| **Map Transform** | `ros2 run tf2_ros tf2_echo map odom` | AMCL correction transform broadcast |
| **Node Lifecycle** | `ros2 lifecycle get /map_server`<br>`ros2 lifecycle get /amcl`<br>`ros2 lifecycle get /controller_server` | Each returns `active [3]` |
| **Nav2 Actions** | `ros2 action list` | Displays `/navigate_to_pose`, `/follow_path`, `/compute_path_to_pose`, `/spin`, `/backup` |

---

## 8. Engineering Challenges, Tuning Decisions, & Verification Scope

1. **Gazebo Core Dump on Robot Spawn**:
   - *Challenge*: Spawning `testbed` caused `gzserver` to immediately terminate with SIGSEGV (signal 11).
   - *Resolution*: Investigating the URDF Xacro trace revealed `<plugin name="control" filename="libgazebo_ros_control.so"/>`. This plugin is an unported ROS 1 binary. Disabling it resolved the crash, as differential drive odometry and velocity control are already completely provided by `libgazebo_ros_diff_drive.so`.
2. **LiDAR Range Calibration for Costmaps**:
   - *Challenge*: The robot's laser has a $1.5\,\text{m}$ maximum range. Using default Nav2 costmap raytracing ($3.0\,\text{m}$) led to costmap clearing anomalies.
   - *Resolution*: Specifically clamped `raytrace_max_range: 1.5`, `obstacle_max_range: 1.5`, and AMCL `laser_max_range: 1.5`.
3. **Modular Lifecycle Node Independence**:
   - *Challenge*: Chaining `map_loader.launch.py` and `localization.launch.py` could cause duplicate `/map_server` node conflicts.
   - *Resolution*: Implemented a `load_map` conditional launch argument in [localization.launch.py](file:///home/zeo/assignment_ws/src/level01_ros_assignment/testbed_navigation/launch/localization.launch.py). By default (`load_map:=false`), it manages only AMCL when `map_loader` is already active, but allows standalone execution via `load_map:=true`.
4. **Honest Scope Disclosure**:
   - *Simulated Environment*: Verification was conducted inside Gazebo Classic 11.10.2 within the provided indoor playground world. Dynamic multi-floor traversal, physical wheel slip on uneven physical terrain, and recovery under complete sensor occlusion were not tested on physical hardware.

---

## 9. Genuine Visual Evidence

All screenshots were captured directly during live system execution and are stored in the [evidence/](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/) directory:

| Screenshot | Stage | Description |
| :--- | :--- | :--- |
| **[01_simulation_bringup.png](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/01_simulation_bringup.png)** | Simulation | RViz showing Testbed-T1.0.0 model, TF frames, and laser scan at spawn |
| **[01_gazebo_simulation.png](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/01_gazebo_simulation.png)** | Gazebo | Gazebo simulator viewport showing playground world and spawned robot |
| **[02_map_loaded.png](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/02_map_loaded.png)** | Map Loading | RViz displaying the loaded $405 \times 400$ 2D occupancy grid |
| **[03_amcl_localized.png](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/03_amcl_localized.png)** | Localization | AMCL particle cloud converged around the localized robot footprint |
| **[04_navigation_moving.png](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/04_navigation_moving.png)** | Navigation | Live navigation execution showing global path plan and costmaps |
| **[04_navigation_goal_reached.png](file:///home/zeo/assignment_ws/src/level01_ros_assignment/evidence/04_navigation_goal_reached.png)** | Navigation | Robot successfully arrived at destination with action `SUCCEEDED` |

---

## 10. Contact Information

- **Name**: Natasha N Bhandari
- **Contact Number**: `+91 9449109766`
- **Email Address**: `nnatashabhandari@gmail.com`
- **Candidate Submission**: Level 1 ROS 2 Navigation Assignment

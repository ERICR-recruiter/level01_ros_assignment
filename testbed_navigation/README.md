# testbed_navigation Package

**Package Name:** `testbed_navigation`  
**Author / Candidate:** MD Akmal  
**Target Platform:** ROS 2 Humble / Gazebo Classic 11 / Ubuntu 22.04  

---

## 1. Overview & Objective

The `testbed_navigation` package provides a **modular, plugin-driven navigation workflow** for the **Testbed-T1.0.0** mobile robot. In accordance with the ERIC Robotics evaluation requirements:
- Rather than calling monolithic `nav2_bringup` scripts, each navigation subsystem is implemented using dedicated launch files and parameter files.
- Each action component (`map_server`, `amcl`, `controller_server`, `planner_server`, `behavior_server`, `bt_navigator`) is directly configured and managed via its corresponding `nav2_lifecycle_manager`.
- The setup supports independent testing, debugging, and verification of map loading, localization, and autonomous navigation.

---

## 2. Package Architecture

```
testbed_navigation/
├── CMakeLists.txt              # Build configuration exporting launch, config, rviz, scripts
├── package.xml                 # Package manifest with all Nav2 dependencies
├── README.md                   # Complete documentation and user guide
├── config/
│   ├── map_server_params.yaml  # Parameters for nav2_map_server (frame_id, topic)
│   ├── amcl_params.yaml        # AMCL parameters (initial pose, particle filter, laser model)
│   └── nav2_params.yaml        # Core Nav2 parameters (costmaps, DWB, NavFn, BT, recoveries)
├── launch/
│   ├── map_loader.launch.py    # Standalone map loading via nav2_map_server
│   ├── localization.launch.py  # Standalone AMCL localization
│   ├── navigation.launch.py    # Manual navigation servers (DWB, NavFn, recoveries, BT)
│   └── full_navigation.launch.py # Convenience launch integrating all components + RViz
├── rviz/
│   └── navigation.rviz         # Pre-configured RViz layout (map, costmaps, particles, TF, goals)
└── scripts/
    └── send_goal.py            # CLI action client to dispatch NavigateToPose goals
```

---

## 3. Subsystem Breakdown

### A. Map Loading (`launch/map_loader.launch.py`)
- **Node:** `nav2_map_server::MapServer`
- **Lifecycle Manager:** `lifecycle_manager_map`
- **Function:** Reads the 405x400 occupancy grid (`testbed_world.yaml` / `testbed_world.pgm`, resolution 0.05m) and publishes the static cost grid on the `/map` topic with `Transient Local` QoS.
- **Parameters:** [`config/map_server_params.yaml`](config/map_server_params.yaml)

### B. Localization (`launch/localization.launch.py`)
- **Node:** `nav2_amcl::AmclNode`
- **Lifecycle Manager:** `lifecycle_manager_localization`
- **Function:** Uses Adaptive Monte Carlo Localization (KLD-sampling particle filter) to estimate robot pose within the static map based on the `/scan` laser scan and `/odom` odometry.
- **Configuration Highlights:**
  - Initial Spawn Pose: `x = 0.0`, `y = 5.0`, `yaw = 0.0 rad`
  - Max Laser Range: `12.0 m` (matches sensor range in fixed URDF)
  - Particles: `min_particles = 500`, `max_particles = 2000`
  - Motion Model: `DifferentialMotionModel`
  - Observation Model: `likelihood_field`
- **Parameters:** [`config/amcl_params.yaml`](config/amcl_params.yaml)

### C. Navigation Core (`launch/navigation.launch.py`)
- **Controller Server:** Runs `dwb_core::DWBLocalPlanner` to compute `/cmd_vel` velocity commands, tracking trajectories while evaluating obstacle collision, path alignment, and goal alignment critics. Includes `local_costmap` (rolling window 3.0m x 3.0m).
- **Planner Server:** Runs `nav2_navfn_planner/NavfnPlanner` to compute Dijkstra/A* global paths from robot pose to the goal across the `global_costmap`.
- **Behavior Server:** Manages recovery actions (`nav2_behaviors`): `Spin`, `BackUp`, `Wait`, `DriveOnHeading`.
- **BT Navigator:** Runs the behavior tree navigator providing the `NavigateToPose` action interface (`/navigate_to_pose`).
- **Lifecycle Manager:** `lifecycle_manager_navigation` orchestrates orderly transition of all four navigation nodes.
- **Parameters:** [`config/nav2_params.yaml`](config/nav2_params.yaml)

---

## 4. Build & Installation

```bash
# 1. Create workspace and clone
mkdir -p ~/assignment_ws/src
cd ~/assignment_ws/src
git clone <your-fork-url>

# 2. Install dependencies
cd ~/assignment_ws
rosdep install --from-paths src --ignore-src -r -y

# 3. Build workspace
colcon build --symlink-install

# 4. Source environment and set DDS
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

---

## 5. Execution Guide

### Option 1: Step-by-Step Modular Bringup (Recommended for Evaluation)

Open separate terminals, each with `source install/setup.bash`:

**Terminal 1 — Launch Gazebo Simulation & Robot:**
```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
*Spawns the test arena in Gazebo, publishes `/robot_description` and TF transforms, and opens base RViz.*

**Terminal 2 — Load Map:**
```bash
ros2 launch testbed_navigation map_loader.launch.py
```
*Verification:*
```bash
ros2 lifecycle get /map_server
# Output: [map_server] active [3]
ros2 topic echo /map --once
```

**Terminal 3 — Run AMCL Localization:**
```bash
ros2 launch testbed_navigation localization.launch.py
```
*Verification:*
```bash
ros2 lifecycle get /amcl
# Output: [amcl] active [3]
ros2 run tf2_ros tf2_echo map odom
# Output: transform close to translation (0.0, 5.0, 0.0)
```

**Terminal 4 — Run Navigation Action Servers:**
```bash
ros2 launch testbed_navigation navigation.launch.py
```
*Verification:*
```bash
ros2 action list
# Output: /navigate_to_pose, /navigate_through_poses, /spin, /backup
```

---

### Option 2: Full Navigation Workflow in One Command

After starting the simulation in Terminal 1, run the combined navigation bringup:
```bash
ros2 launch testbed_navigation full_navigation.launch.py
```
This automatically invokes `map_loader`, `localization`, and `navigation`, and opens RViz pre-configured with the navigation display layout.

---

## 6. Sending Navigation Goals

### A. Via RViz GUI
1. Select the **2D Pose Estimate** tool if you wish to manually re-seed the particle cloud.
2. Select the **2D Goal Pose** (or **Nav2 Goal**) tool from the RViz toolbar.
3. Click and drag anywhere in the arena map (e.g., towards `x = 4.0, y = 2.0`).
4. Observe the global plan, local trajectory rollout, and the robot driving smoothly to the destination.

### B. Via Python CLI Script
```bash
# Navigate to coordinate (x=3.0, y=5.0)
ros2 run testbed_navigation send_goal.py --x 3.0 --y 5.0 --yaw 0.0
```

### C. Via ROS 2 Action CLI
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 5.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

---

## 7. Key Challenges & Solutions

| Challenge | Cause | Resolution |
|---|---|---|
| Robot stalled on velocity commands | Casters had `mu1=0.2` friction causing lateral drag, while drive wheels lacked traction. | Adjusted friction in `testbed.gazebo`: casters `0.001`, wheels `1.0`. |
| AMCL failed to converge in open arena | Lidar range in URDF was restricted to `1.5 m` in a 20m x 20m arena. | Increased lidar range to `12.0 m` in URDF and aligned AMCL & costmap parameters. |
| Time extrapolation errors | `robot_state_publisher` was running on wall time instead of Gazebo `/clock`. | Configured `use_sim_time: True` in `robot_description.launch.py`. |
| Missing map files after build | `maps` folder omitted from `testbed_bringup/CMakeLists.txt` `install()`. | Added `maps` directory to `install()`. |
| RViz model blank on startup | Volatile QoS policy on late-joining subscriber. | Set Durability Policy to `Transient Local` in RViz configuration. |

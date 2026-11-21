# Testbed-T1.0.0 — Modular ROS 2 Navigation (`testbed_navigation`)

A modular **ROS 2 Humble** navigation package for the **Testbed-T1.0.0** differential-drive robot. Rather than relying on the monolithic `nav2_bringup` wrapper, this package manually configures and launches each stage of the Nav2 pipeline—map loading, AMCL localization, and autonomous navigation—using independent launch files, custom parameter configurations, and dedicated lifecycle managers.

---

## Package Structure

```text
ros_nav2_assignment/
├── bugs_fixed.txt                    # Detailed log of all 8 starter code bugs identified and fixed
├── testbed_bringup/                  # Base robot bringup and static map (testbed_world.yaml)
├── testbed_description/              # URDF/Xacro robot model, Gazebo plugins, meshes, RViz config
├── testbed_gazebo/                   # Gazebo world, spawn scripts, and environment models
└── testbed_navigation/               # New modular Nav2 package
    ├── config/
    │   ├── amcl_params.yaml          # AMCL localization parameters
    │   └── nav2_params.yaml          # Planner, controller, costmaps, behaviors, and BT navigator
    ├── launch/
    │   ├── map_loader.launch.py      # Map server + map lifecycle manager
    │   ├── localization.launch.py    # AMCL + localization lifecycle manager
    │   └── navigation.launch.py      # Core Nav2 servers + navigation lifecycle manager
    ├── rviz/                         # Optional saved RViz configuration
    ├── CMakeLists.txt
    ├── package.xml
    └── README.md
```

---

## Architecture & Modular Design

Nav2 servers are implemented as **ROS 2 Lifecycle Nodes**, meaning they start in an `unconfigured` state and must be transitioned to `active` before processing data. To ensure each stage can be launched, tested, or restarted independently without node-name collisions, every launch file pairs its nodes with a uniquely named `nav2_lifecycle_manager`.

### Component Breakdown

| Stage | Launch File | Package / Executable | Key Plugin / Configuration | Lifecycle Manager |
| :--- | :--- | :--- | :--- | :--- |
| **Map Loading** | `map_loader.launch.py` | `nav2_map_server` / `map_server` | Loads `testbed_world.yaml` (`/map`, Transient Local) | `lifecycle_manager_map` |
| **Localization** | `localization.launch.py` | `nav2_amcl` / `amcl` | `nav2_amcl::DifferentialMotionModel`, `likelihood_field`, initial pose `(0.0, 5.0, 0.0)` | `lifecycle_manager_localization` |
| **Global Planning** | `navigation.launch.py` | `nav2_planner` / `planner_server` | `nav2_navfn_planner/NavfnPlanner` on `global_costmap` | `lifecycle_manager_navigation` |
| **Local Control** | `navigation.launch.py` | `nav2_controller` / `controller_server` | `dwb_core::DWBLocalPlanner` on 3m × 3m rolling `local_costmap` | `lifecycle_manager_navigation` |
| **Recoveries** | `navigation.launch.py` | `nav2_behaviors` / `behavior_server` | `Spin`, `BackUp`, `DriveOnHeading`, `Wait` | `lifecycle_manager_navigation` |
| **Orchestration** | `navigation.launch.py` | `nav2_bt_navigator` / `bt_navigator` | Coordinates planning, path following, and recovery Behavior Trees | `lifecycle_manager_navigation` |

### Transform (TF) Tree

```text
map ──(AMCL)──▶ odom ──(Gazebo Diff Drive)──▶ base_footprint ──(robot_state_publisher)──▶ base_link ──▶ lidar_link_1 / wheels / imu_link_1
```

- **Robot Footprint & Costmaps:** Configured with `robot_radius: 0.25` m (derived from the `0.35` m wheel separation in the URDF) and `inflation_radius: 0.45` m (`cost_scaling_factor: 3.0`) to maintain safe clearance around walls and doorways.

---

## Prerequisites

- **OS / ROS 2:** Ubuntu 22.04 with ROS 2 Humble (or `osrf/ros:humble-desktop-full` Docker container)
- **Simulator:** Gazebo Classic 11 (`ros-humble-gazebo-ros-pkgs`) and RViz2
- **Nav2 & Utilities:**

```bash
sudo apt update
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-teleop-twist-keyboard \
  ros-humble-tf2-tools \
  ros-humble-xacro
```

---

## Build Instructions

```bash
mkdir -p ~/assignment_ws/src
cd ~/assignment_ws/src
git clone https://github.com/Yashs2024/level01_ros_assignment.git
cd ~/assignment_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

---

## Running the Navigation Stack

Open four sourced terminals (`source /opt/ros/humble/setup.bash && source ~/assignment_ws/install/setup.bash`) and launch each module in sequence:

### 1. Launch the Gazebo & RViz Simulation

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### 2. Load the Static Map

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

### 3. Start AMCL Localization

```bash
ros2 launch testbed_navigation localization.launch.py
```

### 4. Start the Autonomous Navigation Stack

```bash
ros2 launch testbed_navigation navigation.launch.py
```

---

## Visualizing & Sending Goals in RViz

1. Set **Global Options → Fixed Frame** to `map`.
2. Add the following displays in RViz:
   - **Map** → Topic: `/map` (set **Topic → Durability Policy** to `Transient Local`)
   - **ParticleCloud** → Topic: `/particle_cloud` (set **Topic → Reliability Policy** to `Best Effort`)
   - **Map** → Topic: `/global_costmap/costmap`
   - **Map** → Topic: `/local_costmap/costmap`
   - **Path** → Topic: `/plan`
3. Verify that the `/scan` points align with the map walls (use **2D Pose Estimate** if fine adjustment is needed).
4. Click **2D Goal Pose** in the top toolbar and drag on any reachable point on the map to command the robot.

---

## Starter Code Debugging Summary

Before implementing `testbed_navigation`, a full diagnostic audit of the starter repository uncovered **8 bugs** across CMake build scripts, launch files, URDF/Gazebo plugins, and map metadata. All fixes are documented in detail in `bugs_fixed.txt`:

1. **CMake parse error** (`testbed_description/CMakeLists.txt`): Fixed missing parentheses on `ament_package()`.
2. **Missing map installation** (`testbed_bringup/CMakeLists.txt`): Added `maps` to `install(DIRECTORY ...)`.
3. **Missing model installation** (`testbed_gazebo/CMakeLists.txt`): Added `models` to `install(DIRECTORY ...)`.
4. **Broken map image path** (`testbed_bringup/maps/testbed_world.yaml`): Corrected `wrong_path_testbed_world.pgm` to `testbed_world.pgm`.
5. **Malformed XML tag** (`testbed_description/urdf/testbed.gazebo`): Removed stray `>` on `</initial_orientation_as_reference>>`.
6. **Short LiDAR range** (`testbed_description/urdf/testbed.gazebo`): Increased `<max>` range from `1.5` m to `12.0` m so `/scan` detects room walls instead of returning `.inf`.
7. **Launch executable typo** (`testbed_description/launch/robot_description.launch.py`): Corrected `robot_state_publishe` to `robot_state_publisher`.
8. **Missing simulation clock** (`testbed_description/launch/robot_description.launch.py`): Added `{'use_sim_time': True}` to `robot_state_publisher`.

---

## Challenges Faced & Solutions

- **TF Timestamp Mismatch (`use_sim_time`):** `robot_state_publisher` initially ran on system wall-clock time while Gazebo published `/scan` and `/odom` on `/clock`. Enforcing `use_sim_time: True` across all simulation and Nav2 nodes eliminated TF extrapolation errors.
- **AMCL Starved of Features:** With the starter LiDAR capped at `1.5` m, scans in open areas returned `.inf`. Increasing the ray sensor's maximum range to `12.0` m and matching `laser_max_range` in `amcl_params.yaml` enabled reliable scan matching.
- **RViz QoS Policies in ROS 2 Humble:** `/map` and `/particle_cloud` initially failed to render in RViz until their topic QoS settings were matched to Nav2's publishers (`Transient Local` durability for `/map` and `Best Effort` reliability for `/particle_cloud`).
- **Initial Pose Alignment:** Inspecting `spawn_testbed.launch.py` showed the robot spawns at `(0.0, 5.0, 0.0)` rather than the map origin `(0.0, 0.0, 0.0)`. Setting `set_initial_pose: true` with `y: 5.0` in `amcl_params.yaml` allowed immediate localization on startup.

---

## Demo

- **Video Demonstration:**

https://github.com/user-attachments/assets/66178076-9f2d-48be-909c-2dd2ed490d81


- **Screenshots:**
  - **Localization (AMCL + Map + LaserScan alignment):**

    !<img width="1920" height="1028" alt="Localization" src="https://github.com/user-attachments/assets/640dac40-f026-42a0-b4ce-6a4a95c8e026" />
  - **Autonomous Navigation (Global/Local Costmaps + Path):**

    !<img width="1920" height="982" alt="Navigation" src="https://github.com/user-attachments/assets/10286c20-9102-4b44-a631-41e6b5a94c5d" />

---

## Contact Information

- **Name:** Yash Arun Surve
- **Contact Number:** [7972308355]
- **Email Address:** [yashsurve2257@gmail.com]

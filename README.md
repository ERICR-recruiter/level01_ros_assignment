# Level 1: ROS2 Navigation Assignment - Rithvik Bhaskar

## Overview
At ERIC Robotics, modularity is key. The ROS 2 `nav2` stack reflects this perfectly with a flexible, plugin-based framework, allowing independent operation of each navigation component. In this assignment, the navigation workflow for the **Testbed-T1.0.0** mobile robot has been built from the ground up by directly interfacing with individual `nav2` action servers and lifecycle-managed plugins rather than a monolithic bringup.

All intentional bugs in the starter code have been diagnosed and resolved (documented in detail in [`bugs_identified_and_fixes.txt`](bugs_identified_and_fixes.txt)), and a dedicated [`testbed_navigation`](testbed_navigation) package has been implemented to handle modular map loading, AMCL probabilistic localization, and autonomous navigation.

---

## Summary of Fixed Starter Code Bugs
A comprehensive report is provided in [`bugs_identified_and_fixes.txt`](bugs_identified_and_fixes.txt). Key fixes include:
1. **Map Loading Failure (`testbed_bringup/maps/testbed_world.yaml`)**:
   Fixed map image filename from incorrect placeholder `wrong_path_testbed_world.pgm` to `testbed_world.pgm`.
2. **CMake Build Failure (`testbed_description/CMakeLists.txt`)**:
   Added missing parentheses to `ament_package()`.
3. **Missing Map Assets in Install (`testbed_bringup/CMakeLists.txt`)**:
   Added `maps` directory to the CMake install rule so maps are properly deployed to `share/testbed_bringup/maps`.
4. **Missing Models Assets in Install (`testbed_gazebo/CMakeLists.txt`)**:
   Added `models` directory to the CMake install rule so Gazebo can discover playground model assets.
5. **Obsolete ROS 1 Plugin (`testbed_description/urdf/testbed.gazebo`)**:
   Removed legacy `libgazebo_ros_control.so` which threw load failures in ROS 2 Gazebo.
6. **XML Syntax Error (`testbed_description/urdf/testbed.gazebo`)**:
   Removed duplicate closing bracket `>>` on `<initial_orientation_as_reference>`.
7. **LiDAR Range Truncation (`testbed_description/urdf/testbed.gazebo`)**:
   Increased Hokuyo LiDAR max range from `1.5m` to `12.0m` (360 samples) so the robot can perceive walls across the 15m environment for localization and obstacle avoidance.
8. **Caster Wheel Friction Drag (`testbed_description/urdf/testbed.gazebo`)**:
   Reduced fixed caster wheel friction from `mu1=0.2, mu2=0.2` to `0.001` (virtually frictionless) and set drive wheel traction to `1.0`, enabling smooth differential rotation without freezing.
9. **Robot State Publisher Sim Time Desync (`testbed_description/launch/robot_description.launch.py`)**:
   Added `use_sim_time: True` to ensure TF timestamps synchronize with Gazebo's `/clock`.

---

## Package Structure

```
ros_nav2_assignment/
├── bugs_identified_and_fixes.txt   # Detailed log of identified bugs and resolutions
├── testbed_description/            # URDF, meshes, and robot state publisher
├── testbed_gazebo/                 # Gazebo simulation worlds and models
├── testbed_bringup/                # Full bringup launch file and occupancy grid map
├── testbed_navigation/             # Modular Nav2 navigation package
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── README.md
│   ├── config/
│   │   ├── amcl_params.yaml        # AMCL localization parameters
│   │   └── nav2_params.yaml        # Controller, planner, behaviors, costmaps & BT parameters
│   └── launch/
│       ├── map_loader.launch.py    # Map server lifecycle node
│       ├── localization.launch.py  # AMCL localization & map server
│       ├── navigation.launch.py    # Controller, Planner, Behavior Server, BT Navigator
│       └── testbed_navigation_all.launch.py # Complete integrated navigation stack
├── help.md                         # Guidelines and FAQs
└── README.md                       # Main assignment documentation
```

---

## Modular Nav2 Plugin Implementation

The `testbed_navigation` package directly leverages the following Nav2 plugins:

| Subsystem | Plugin / Node | Description |
| :--- | :--- | :--- |
| **Map Server** | `nav2_map_server::MapServer` | Loads occupancy grid map and serves `/map` topic via `nav2_lifecycle_manager`. |
| **Localization** | `nav2_amcl::AmclNode` | Adaptive Monte Carlo Localization using `nav2_amcl::DifferentialMotionModel` and likelihood field laser model. Seeding at `(0, 5, 0)` matching spawn position. |
| **Global Planner** | `nav2_navfn_planner/NavfnPlanner` | Computes optimal collision-free global path in `planner_server` using `global_costmap` (`StaticLayer`, `ObstacleLayer`, `InflationLayer`). |
| **Local Planner** | `dwb_core::DWBLocalPlanner` | Generates dynamically feasible velocity trajectories in `controller_server` using `local_costmap` (`VoxelLayer`, `InflationLayer`). |
| **Behaviors** | `nav2_behaviors::BehaviorServer` | Provides recovery actions (`Spin`, `BackUp`, `DriveOnHeading`, `Wait`). |
| **Orchestration** | `nav2_bt_navigator::BtNavigator` | Executes behavior trees for navigation to pose with automated replanning and recovery fallbacks. |

---

## Instructions to Run & Verify

### 1. Build the Workspace
```bash
mkdir -p ~/assignment_ws/src
cd ~/assignment_ws/src
# Clone your fork:
git clone <your-fork-url> .
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
```

### 2. Launch Simulation Environment
In Terminal 1:
```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
*Gazebo will launch with the testbed playground and spawn the Testbed-T1.0.0 robot at `(0.0, 5.0, 0.0)`. RViz will open.*

### 3. Launch Navigation Subsystems

#### Method 1: Component-by-Component (Modular Verification)
- **Step A: Load Map**
  ```bash
  ros2 launch testbed_navigation map_loader.launch.py
  ```
  *Verify `/map` topic is published and visible in RViz.*

- **Step B: Start Localization**
  ```bash
  ros2 launch testbed_navigation localization.launch.py
  ```
  *AMCL activates, aligns particles around `(0.0, 5.0)`, and publishes `map -> odom` transform.*

- **Step C: Start Navigation Action Workflow**
  ```bash
  ros2 launch testbed_navigation navigation.launch.py
  ```
  *Action servers `/navigate_to_pose`, `/follow_path`, `/compute_path_to_pose` become active.*

#### Method 2: All-in-One Navigation Launch
```bash
ros2 launch testbed_navigation testbed_navigation_all.launch.py
```

### 4. Sending Navigation Goals
- **Via RViz GUI**: Click the **"2D Goal Pose"** button in RViz and select a destination point on the map.
- **Via CLI Action Client**:
  ```bash
  ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
    "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
  ```

---

## Contact Info
- **Name**: Rithvik Bhaskar
- **Email Address**: crithvikbhaskar@gmail.com / rithv_urh7
- **GitHub**: [crithvikbhaskar](https://github.com/crithvikbhaskar)

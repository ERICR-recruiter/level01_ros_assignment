# testbed_navigation

A modular ROS 2 Humble navigation package developed for the **Testbed-T1.0.0** mobile robot (differential drive) for the **ERIC Robotics** technical evaluation.

---

## 1. Package Architecture & Approach

Rather than relying on a monolithic `nav2_bringup` configuration, `testbed_navigation` implements a modular, decoupled architecture adhering to ROS 2 Nav2 plugin design patterns. Each navigation subsystem is isolated into dedicated parameter files and launch scripts managed via ROS 2 lifecycle managers.

```
testbed_navigation/
├── CMakeLists.txt              # Build configuration and asset installation
├── package.xml                 # Package manifest and Nav2 plugin dependencies
├── README.md                   # Package documentation
├── config/
│   ├── amcl_params.yaml        # AMCL probabilistic localization parameters
│   └── nav2_params.yaml        # Global/Local planners, costmaps, and behavior tree configs
└── launch/
    ├── map_loader.launch.py    # Loads map_server and transitions lifecycle to active
    ├── localization.launch.py  # Launches AMCL and map_server with lifecycle management
    ├── navigation.launch.py    # Launches controller, planner, behaviors, BT navigator & lifecycle
    └── testbed_navigation_all.launch.py # Top-level launch file orchestrating all nodes
```

---

## 2. Nav2 Plugin Selection & Configuration

### A. Map Loading (`map_loader.launch.py`)
- **Plugin / Node**: `nav2_map_server::MapServer` (`nav2_map_server/map_server`)
- **Lifecycle Management**: Managed by `nav2_lifecycle_manager::LifecycleManager`. The node automatically transitions from `unconfigured` to `inactive` to `active`, serving `/map` and the `/map_server/load_map` service.
- **Map File**: Uses the 0.05m resolution occupancy grid map provided in `testbed_bringup/maps/testbed_world.yaml`.

### B. Localization (`localization.launch.py`)
- **Plugin / Node**: `nav2_amcl::AmclNode` (`nav2_amcl/amcl`)
- **Motion Model**: `nav2_amcl::DifferentialMotionModel` matching the two-wheel differential drive kinematics of Testbed-T1.0.0.
- **Laser Model**: `likelihood_field` with 60 max beams and range of 0.1m - 12.0m.
- **Initial Pose**: Automatically seeded at `(x: 0.0, y: 5.0, yaw: 0.0)` matching the Gazebo spawn position in `spawn_testbed.launch.py`.

### C. Global Path Planning
- **Plugin**: `nav2_navfn_planner/NavfnPlanner` (Dijkstra / A* navigation function) configured in `planner_server`.
- **Costmap**: `global_costmap` incorporating:
  - `StaticLayer`: Ingests the global static map from `/map`.
  - `ObstacleLayer`: 2D obstacle marking and raytracing from LiDAR scan (`/scan`).
  - `InflationLayer`: Exponential cost decay with robot radius 0.22m and inflation radius 0.55m.

### D. Local Trajectory Generation & Control
- **Plugin**: `dwb_core::DWBLocalPlanner` in `controller_server`.
- **Critics Evaluated**: `RotateToGoal`, `Oscillation`, `BaseObstacle`, `GoalAlign`, `PathAlign`, `PathDist`, `GoalDist`.
- **Velocity Limits**: Max linear velocity: 0.26 m/s, Max angular velocity: 1.0 rad/s, Decel limit: -2.5 m/s².
- **Costmap**: `local_costmap` operating with a rolling window (3m x 3m) in the `odom` frame using a `VoxelLayer` and `InflationLayer`.

### E. Recovery & Behavior Trees
- **Behaviors**: `nav2_behaviors::BehaviorServer` hosting `Spin`, `BackUp`, `DriveOnHeading`, and `Wait`.
- **Behavior Tree**: `nav2_bt_navigator` orchestrating fallback recovery behaviors, replanning upon path blockages, and progress checking.

---

## 3. How to Build & Run

### Step 1: Build the Workspace
```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
```

### Step 2: Launch the Base Simulation
In Terminal 1:
```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
This spawns the Testbed-T1.0.0 robot into the Gazebo playground world and opens RViz.

### Step 3: Run Navigation Components

You can run individual components independently or all together:

#### Option A: Run Components Individually (Modular Workflow)
1. **Load Map Server**:
   ```bash
   ros2 launch testbed_navigation map_loader.launch.py
   ```
2. **Launch AMCL Localization**:
   ```bash
   ros2 launch testbed_navigation localization.launch.py
   ```
3. **Launch Nav2 Action Workflow**:
   ```bash
   ros2 launch testbed_navigation navigation.launch.py
   ```

#### Option B: Run Full Navigation Stack
```bash
ros2 launch testbed_navigation testbed_navigation_all.launch.py
```

### Step 4: Send Navigation Goals
- In RViz, click **"2D Goal Pose"** in the top toolbar and click anywhere on the free space in the map.
- Alternatively, send a goal via the ROS 2 Action CLI:
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

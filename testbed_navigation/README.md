# `testbed_navigation` ROS 2 Package

Autonomous modular navigation framework for the **Testbed-T1.0.0** differential drive robot developed by **ERIC Robotics**, built with **ROS 2 Humble** and the **Nav2** stack.

---

## Architecture Overview

In adherence to ERIC Robotics' modular software design principles, this package does **not** rely on monolithic bringup scripts (such as `nav2_bringup`). Instead, it decomposes the autonomous navigation pipeline into **three decoupled, individually managed lifecycle modules**:

```
                                    +-----------------------------------------+
                                    |        ROS 2 Navigation Pipeline        |
                                    +-----------------------------------------+
                                                         |
         +-----------------------------------------------+-----------------------------------------------+
         |                                               |                                               |
         v                                               v                                               v
+------------------------+                   +------------------------+                     +------------------------+
|   1. Map Loader        |                   |   2. Localization      |                     |   3. Navigation Stack  |
+------------------------+                   +------------------------+                     +------------------------+
| Node: nav2_map_server  |                   | Node: nav2_amcl        |                     | Servers:               |
| Lifecycle:             |                   | Lifecycle:             |                     |  - planner_server      |
|   lifecycle_manager    |                   |   lifecycle_manager    |                     |  - controller_server   |
| Topic: /map            |                   | Filter: Particle Cloud |                     |  - behavior_server     |
| Service: /map_server/* |                   | Topic: /initialpose    |                     |  - bt_navigator        |
+------------------------+                   +------------------------+                     | Lifecycle:             |
                                                                                            |   lifecycle_manager    |
                                                                                            | Topics: /cmd_vel, etc. |
                                                                                            +------------------------+
```

### Nav2 Plugin Selections & Technical Rationale

1. **Map Server (`nav2_map_server`)**:
   - Loads the 2D occupancy grid (`testbed_world.yaml` + `testbed_world.pgm`, 0.05 m resolution).
   - Paired with an independent `nav2_lifecycle_manager` (`autostart: true`) managing `['map_server']` to transition it to `active`.

2. **Localization (`nav2_amcl`)**:
   - Motion Model: `nav2_amcl::DifferentialMotionModel` matching the two-wheeled differential drive kinematics of Testbed-T1.0.0.
   - Sensor Model: `likelihood_field` with 60 beams and 500–2000 particle dynamic filter size.
   - Laser Range: 0.1 m to 12.0 m, tuned to detect the 20m x 20m simulated playground arena.
   - Lifecycle: Managed independently by `lifecycle_manager_localization` (`node_names: ['amcl']`).

3. **Global Planner (`nav2_planner`)**:
   - Plugin: `nav2_navfn_planner/NavfnPlanner`
   - Uses Dijkstra wave-expansion to compute smooth, global optimal collision-free paths from the robot's current pose to the goal pose across the global costmap.

4. **Local Controller / Trajectory Generator (`nav2_controller`)**:
   - Plugin: `dwb_core::DWBLocalPlanner` (Dynamic Window Approach)
   - Velocity limits: Max forward speed $0.35\text{ m/s}$, rotational speed $1.0\text{ rad/s}$.
   - Critics enabled:
     - `RotateToGoal`: Orients the robot towards the target heading upon reaching goal vicinity.
     - `Oscillation`: Prevents limit cycles / rapid back-and-forth steering.
     - `BaseObstacle`: Heavily penalizes trajectories colliding with costmap obstacles.
     - `PathAlign` & `GoalAlign`: Guides trajectories towards global path and final goal orientation.
     - `PathDist` & `GoalDist`: Balances path adherence against distance progress.

5. **Behavior Trees & Recovery (`nav2_bt_navigator` & `nav2_behaviors`)**:
   - Behavior Tree Engine: `nav2_bt_navigator/NavigateToPoseNavigator` executing `navigate_to_pose_w_replanning_and_recovery.xml`.
   - Recovery Behaviors: `spin` (`Spin`), `backup` (`BackUp`), and `wait` (`Wait`) via `behavior_server` to untangle the robot if localized obstacles block all paths.

6. **Costmaps (`nav2_costmap_2d`)**:
   - Robot Physical Radius: $0.25\text{ m}$ ($25\text{ cm}$), accurately enveloping the robot chassis and caster wheel base.
   - Local Costmap: $3\text{m} \times 3\text{m}$ rolling window on `odom` frame using voxel and inflation layers.
   - Global Costmap: Full map static layer + dynamic obstacle marking/clearing from `/scan` + inflation layer ($0.55\text{ m}$ radius).

---

## Package Structure

```
testbed_navigation/
├── CMakeLists.txt                    # CMake build configuration and install rules
├── package.xml                       # Package metadata and Nav2 dependencies
├── README.md                         # Architecture, usage, and verification guide
├── config/
│   ├── amcl_params.yaml              # Tuned AMCL localization parameters
│   └── nav2_params.yaml              # Planners, controllers, costmaps, BT parameters
└── launch/
    ├── map_loader.launch.py          # Module 1: map_server + lifecycle manager
    ├── localization.launch.py        # Module 2: amcl + lifecycle manager
    ├── navigation.launch.py          # Module 3: planner/controller/BT/behaviors + lifecycle
    └── testbed_navigation_bringup.launch.py # Integrated launch coordinating all modules
```

---

## Step-by-Step Instructions

### Step 0: Build the Workspace

In your terminal:
```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
```

---

### Step 1: Launch the Simulation Environment

Open **Terminal 1**:
```bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
* Gazebo will load the playground world and spawn the Testbed-T1.0.0 robot at $(0, 0, 0.05)$.
* RViz will open showing the robot model and the active laser scan (`/scan`).

---

### Step 2: Load the Map

Open **Terminal 2**:
```bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation map_loader.launch.py
```
* `map_server` loads `testbed_bringup/maps/testbed_world.yaml`.
* In RViz: Add a **Map** display and set topic to `/map`. You will see the complete playground floorplan loaded.

---

### Step 3: Run Localization (AMCL)

Open **Terminal 3**:
```bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation localization.launch.py
```
* `amcl` starts and configures its particle filter.
* In RViz:
  1. Set the **Global Options -> Fixed Frame** to `map`.
  2. Add a **PoseWithCovariance** display listening to `/amcl_pose` (or **ParticleCloud** on `/particlecloud`).
  3. Click **2D Pose Estimate** in the top toolbar and click/drag on the robot's location $(0, 0)$.
  4. The particle cloud will snap tightly around the robot's physical position.

---

### Step 4: Run Autonomous Navigation

Open **Terminal 4**:
```bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```
* `controller_server`, `planner_server`, `behavior_server`, and `bt_navigator` initialize and transition to `active`.
* In RViz:
  1. Add a **Path** display on `/plan` (global path).
  2. Add **Path** display on `/local_plan` (local trajectory).
  3. Add **Map** display on `/global_costmap/costmap` and `/local_costmap/costmap`.
  4. Click **2D Goal Pose** on the RViz toolbar and click any free space location inside the room.
  5. The robot will compute a global path, avoid obstacles, and drive autonomously to the destination!

*(Alternative: You can also launch all three navigation modules simultaneously with:)*
```bash
ros2 launch testbed_navigation testbed_navigation_bringup.launch.py
```

---

## Challenges Encountered & Resolutions

| Challenge | Root Cause | Resolution |
| :--- | :--- | :--- |
| **`colcon build` parse failure** | `ament_package` lacked parentheses `()` in `testbed_description/CMakeLists.txt`. | Added `()` to make it `ament_package()`. |
| **Missing map in install tree** | `testbed_bringup/CMakeLists.txt` only installed `launch`, skipping `maps`. | Added `maps` directory to the `install` rule. |
| **Map load crash** | `testbed_world.yaml` had `wrong_path_testbed_world.pgm`. | Corrected image filename to `testbed_world.pgm`. |
| **Missing world meshes** | `testbed_gazebo/CMakeLists.txt` did not install `models`. | Added `models` to the `install` rule. |
| **LiDAR blindness** | Ray sensor range in URDF was capped at `1.5 m` for a 20m arena. | Increased ray sensor range to `12.0 m` for full visibility. |
| **TF timestamp rejection** | `robot_description.launch.py` omitted `use_sim_time: True`. | Added `use_sim_time: true` to synchronize TF with Gazebo clock. |
| **Ground collision on spawn** | Robot spawned at $Z=0.0$ sinking into ground plane. | Set default spawn elevation to $Z=0.05$ with configurable arguments. |
| **Stray XML tokens** | IMU sensor plugin had extra `>` character in `testbed.gazebo`. | Cleaned XML syntax. |
| **Robot slip in Gazebo vs RViz** | Fixed casters had $\mu=0.2$ acting as brakes while drive wheels slipped in Gazebo. | Set caster friction to $\mu=0.001$ and drive wheels to $\mu=10.0$ with adequate torque. |
| **Doorway navigation blocked** | Inflation radius $0.55\text{ m}$ overlapping in $0.85\text{ m}$ doorways. | Reduced inflation to $0.25\text{ m}$ with exponential decay (`cost_scaling_factor: 8.0`). |
| **TF extrapolation into past** | Tight default transform tolerances (0.1s) under simulation load caused TF lookup failures. | Increased transform tolerance to $1.0\text{ s}$ across planners, costmaps, and controllers. |

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
   - Sensor Model: `likelihood_field` with 120 beams and 500–2000 particle dynamic filter size (`update_min_d: 0.05`, `update_min_a: 0.05`).
   - Laser Range: 0.1 m to 12.0 m, tuned to detect the 20m x 20m simulated playground arena.
   - Lifecycle: Managed independently by `lifecycle_manager_localization` (`node_names: ['amcl']`).

3. **Global Planner (`nav2_planner`)**:
   - Plugin: `nav2_navfn_planner/NavfnPlanner` (`use_astar: false`)
   - Uses Dijkstra wave-expansion to reliably compute smooth, global optimal collision-free paths from the robot's current pose to the goal pose across the global costmap.

4. **Local Controller (`nav2_controller`)**:
   - Plugin: `nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController`
   - Velocity limits: Desired forward speed $0.35\text{ m/s}$, rotational speed $1.0\text{ rad/s}$.
   - Features enabled:
     - Arc-length velocity-scaled lookahead (`0.30 m` – `0.80 m`) ensuring the controller stays strictly on the path without being misled by U-turns behind walls.
     - `use_regulated_linear_velocity_scaling` & `use_cost_regulated_linear_velocity_scaling`: Smoothly slows down around tight doorway turns and near wall inflation.
     - `use_rotate_to_heading`: Rotates cleanly in place when angular heading error exceeds `0.785 rad`.
     - `use_collision_detection`: Validates forward arc clearance against `local_costmap`.

5. **Behavior Trees, Goal Relay & Recovery (`nav2_bt_navigator` & `nav2_behaviors`)**:
   - Behavior Tree Engine: `nav2_bt_navigator/NavigateToPoseNavigator` executing `navigate_to_pose_w_replanning_and_recovery.xml`.
   - `goal_pose_relay.py`: Transforms incoming `/goal_pose` goals (e.g., clicked in RViz under `odom` Fixed Frame) into `map` frame once on receipt so multi-room plans never trigger 10-second TF extrapolation timeouts.
   - Recovery Behaviors: `spin` (`Spin`), `backup` (`BackUp`), and `wait` (`Wait`) via `behavior_server`.

6. **Costmaps (`nav2_costmap_2d`)**:
   - Robot Physical Radius: $0.24\text{ m}$ ($24\text{ cm}$), enveloping the asymmetric right wheel (`-0.241 m`) and rear chassis while maintaining ~0.37 m clearance inside 0.85–0.90 m doorways.
   - Local Costmap: $4\text{m} \times 4\text{m}$ rolling window on `odom` frame (`obstacle_layer` + `inflation_layer`, `inflation_radius: 0.40 m`, `cost_scaling_factor: 4.0`).
   - Global Costmap: Full map static layer + dynamic obstacle marking/clearing from `/scan` + inflation layer (`0.40 m` radius, `cost_scaling_factor: 4.0`).

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
├── scripts/
│   └── goal_pose_relay.py            # Converts /goal_pose from odom to map frame once
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
| **Robot slip in Gazebo vs RViz** | Fixed casters had $\mu=0.2$ acting as brakes; `wheel_separation` was $0.35\text{ m}$ instead of $0.376\text{ m}$. | Set caster friction to $\mu=0.001$, drive wheels to $\mu=10.0$, corrected separation to $0.376\text{ m}$ with $20\text{ N}\cdot\text{m}$ torque. |
| **Doorway & U-turn stalls** | Inflation $0.55\text{ m}$ closed $0.9\text{ m}$ doors; DWB `GoalDist` locked onto paths behind walls. | Set `robot_radius: 0.24 m`, `inflation_radius: 0.40 m` (`cost_scaling_factor: 4.0`), and switched to `RegulatedPurePursuitController`. |
| **TF extrapolation into past** | RViz `2D Goal Pose` under `odom` Fixed Frame exceeded 10s TF history on multi-room routes. | Added `goal_pose_relay.py` to convert goals into `map` frame on receipt and set `transform_tolerance: 1.0 s`. |

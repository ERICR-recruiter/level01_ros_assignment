# testbed_navigation

ROS 2 Humble navigation package developed for the **Testbed-T1.0.0** differential drive mobile robot. 

Rather than relying on the monolithic `nav2_bringup` wrapper, this package provides a completely modular Nav2 pipeline where map loading, AMCL localization, and path planning/control are decoupled into independent launch files, parameter sets, and lifecycle managers.

Author: **Rajrajeshwar Pandya** (<rajrajeshwarpand108@gmail.com>)

---

## 1. Package Structure

```
testbed_navigation/
├── CMakeLists.txt              # Build and install targets
├── package.xml                 # Package dependencies (nav2 plugins, rviz2, etc.)
├── README.md                   # Approach report and testing instructions
├── config/
│   ├── amcl_params.yaml        # AMCL parameters & initial pose configuration
│   └── nav2_params.yaml        # Costmaps, DWB controller, Navfn planner, BT, smoother
├── launch/
│   ├── map_loader.launch.py    # Standalone map server with dedicated lifecycle manager
│   ├── localization.launch.py  # AMCL localization (supports standalone or chained map_server)
│   └── navigation.launch.py    # Core Nav2 stack (planner, controller, BT, recoveries)
├── rviz/
│   └── nav2_default_view.rviz  # Preconfigured RViz display for localization & path visualization
└── scripts/                    # Helper scripts
```

---

## 2. Approach & Architecture

The assignment requirement is to build a modular navigation stack without `nav2_bringup`. To achieve this, each component was set up with independent lifecycle control and clean topic remappings:

### 2.1 Map Loading (`launch/map_loader.launch.py`)
- Spins up `nav2_map_server/map_server` loading the occupancy grid from `testbed_bringup/maps/testbed_world.yaml`.
- Uses a lightweight `nav2_lifecycle_manager` (`lifecycle_manager_map_server`) with `autostart: true` to configure and activate `map_server`.
- Map is published with `TRANSIENT_LOCAL` QoS durability on `/map`.

### 2.2 Localization (`launch/localization.launch.py`)
- Employs `nav2_amcl/amcl` tuned with `DifferentialMotionModel` to handle differential drive kinematics.
- Configured coordinate frames:
  - Global: `map`
  - Odometry: `odom`
  - Base: `base_footprint`
  - LaserScan: `scan`
- **Initial Pose Automation**: Configured `set_initial_pose: true` at `(x: 0.0, y: 5.0, yaw: 0.0)` in `amcl_params.yaml` matching the Gazebo spawn coordinates. This means the robot immediately initializes its particle cloud upon launch without requiring manual "2D Pose Estimate" clicking in RViz.
- **Modularity Feature**: Includes a launch argument `start_map_server:=true|false`. If map_server was already launched independently via `map_loader.launch.py`, setting `start_map_server:=false` runs AMCL cleanly on its own.

### 2.3 Navigation & Control (`launch/navigation.launch.py`)
- **Global Planning**: `nav2_navfn_planner/NavfnPlanner` running on a 20Hz loop using static map data, laser obstacle markings, and obstacle inflation.
- **Local Control**: `dwb_core::DWBLocalPlanner` with trajectory critic scoring (`BaseObstacle`, `PathAlign`, `GoalAlign`, `PathDist`, `GoalDist`, `RotateToGoal`).
- **Velocity Smoothing**: Integrated `nav2_velocity_smoother` intercepting `/cmd_vel_nav` from the controller and outputting smooth kinematic accelerations to `/cmd_vel` to prevent wheel slippage.
- **Behavior Tree & Recoveries**: `bt_navigator` and `behavior_server` providing automated spin, backup, and wait recovery behaviors if the robot gets close to obstacles or encounters local minima.
- **Lifecycle Coordination**: A dedicated `lifecycle_manager_navigation` synchronously transitions all servers (`controller_server`, `planner_server`, `behavior_server`, `bt_navigator`, `smoother_server`, `velocity_smoother`) into their active states.

---

## 3. Challenges Faced & Debugging Process

During the implementation and testing in Gazebo, I ran into several distinct issues across the starter code, simulation physics, and ROS 2 middleware:

### Challenge 1: The Robot Drifting & Skidding During Turns (Caster Friction Bug)
- **Observation**: When commanded to turn or follow a trajectory, the robot visibly slid across the floor, and the RViz laser scan drastically rotated out of phase with the actual map walls.
- **Root Cause**: In `testbed_description/urdf/testbed.gazebo`, the 4 fixed caster wheels had friction coefficients set to `mu1=0.2, mu2=0.2`, while the drive wheels also had weak `0.2` friction. Because the caster joints in the URDF are `<joint type="fixed">`, they weren't free-spinning wheels—they acted like rubber brake pads dragging on the ground. This dragged the chassis, caused the drive wheels to spin out, corrupted the wheel odometry (`/odom`), and caused AMCL to diverge.
- **Solution**: Set the caster wheel friction to `mu1=0.0, mu2=0.0` (frictionless sliding casters) and gave the drive wheels proper traction with `mu1=1.0, mu2=1.0`. Immediately, the robot turned crisply and odometry remained locked with simulation truth.

### Challenge 2: RViz Transform Cache Warning (`TF_OLD_DATA`)
- **Observation**: RViz printed continuous warnings: `"Message Filter dropping message: ... timestamp on the message is earlier than all the data in the transform cache"`, and laser scans flickered.
- **Root Cause**: `robot_description.launch.py` started `robot_state_publisher` without passing `use_sim_time: True`. As a result, TF frames (`base_link`, `lidar_link_1`) were timestamped with Linux system wall clock time, whereas Gazebo and the LIDAR plugin published messages stamped with Gazebo simulation clock time (`/clock`).
- **Solution**: Updated `robot_description.launch.py` to declare and pass `{'use_sim_time': use_sim_time}` to `robot_state_publisher`.

### Challenge 3: Blind Spots Due to 1.5m LIDAR Max Range
- **Observation**: When the robot spawned in the middle of the room, AMCL particles scattered randomly and the robot could not localize itself.
- **Root Cause**: In `testbed.gazebo`, the ray sensor `<max>` range was set to only `1.5` meters. In a room measuring over 10m across, the sensor rays never reached the walls from the room center.
- **Solution**: Expanded the ray sensor `<max>` range in `testbed.gazebo` to `12.0` meters and matched `laser_max_range: 12.0` in `amcl_params.yaml`.

### Challenge 4: Missing Package Installation Directives
- **Observation**: `map_server` could not find `testbed_world.yaml` after `colcon build`, and Gazebo warned about missing `test_room` models.
- **Root Cause**: `testbed_bringup/CMakeLists.txt` omitted the `maps` folder from the `install(DIRECTORY ...)` target, and `testbed_gazebo/CMakeLists.txt` omitted `models`. In addition, `testbed_world.yaml` had a typo pointing to `wrong_path_testbed_world.pgm`.
- **Solution**: Added the install rules to both `CMakeLists.txt` files and fixed the path in `testbed_world.yaml`.

### Challenge 5: FastDDS Node Discovery & Lifecycle Transitions
- **Observation**: Running launch files in multiple terminals occasionally produced lifecycle transition errors (`Unable to start transition 101: invalid data size`) and dropped topic subscriptions.
- **Root Cause**: Default FastDDS under heavy message volume and multiple lifecycle managers in separate shells suffered discovery timeouts.
- **Solution**: Switched to Cyclone DDS (`export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`), which handled multi-terminal discovery and lifecycle states flawlessly.

---

## 4. How to Run and Test

### Prerequisites
Make sure dependencies are installed and the workspace is built:
```bash
sudo apt install -y ros-humble-cyclonedds ros-humble-rmw-cyclonedds-cpp ros-humble-navigation2 ros-humble-nav2-bringup
cd ~/assignment_ws
colcon build
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

### Option A: Testing Individual Modular Components

**1. Standalone Map Server:**
```bash
ros2 launch testbed_navigation map_loader.launch.py use_sim_time:=false
# Verify:
ros2 topic echo /map --once
```

**2. Simulation + AMCL Localization:**
```bash
# Terminal 1: Simulation + RViz
ros2 launch testbed_bringup testbed_full_bringup.launch.py rvizconfig:=$(ros2 pkg prefix testbed_navigation)/share/testbed_navigation/rviz/nav2_default_view.rviz

# Terminal 2: AMCL (bundled with map server)
ros2 launch testbed_navigation localization.launch.py start_map_server:=true
```

---

### Option B: Full Autonomous Navigation Stack (Recommended Test)

Run the following three commands in separate terminals:

**Terminal 1 — Bring up Gazebo Simulation & RViz:**
```bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py rvizconfig:=$(ros2 pkg prefix testbed_navigation)/share/testbed_navigation/rviz/nav2_default_view.rviz
```

**Terminal 2 — Bring up Localization (AMCL + Map Server):**
```bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation localization.launch.py start_map_server:=true
```

**Terminal 3 — Bring up Navigation Stack (Planners, Controllers, BT):**
```bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```

### Sending Navigation Goals:
1. In RViz, select the **2D Goal Pose** tool in the top toolbar.
2. Click anywhere on the map (e.g. through a doorway or into another room) and drag the green arrow to set the desired heading.
3. Observe the global path (Navfn) and local trajectory (DWB) in RViz as the robot navigates around obstacles to the goal.

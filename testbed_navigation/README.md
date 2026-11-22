# testbed_navigation

Modular ROS2 Humble navigation package for the ERIC Robotics **Testbed-T1.0.0** robot. Instead of calling `nav2_bringup`, each stage of the Nav2 pipeline—map serving, AMCL localization, and autonomous navigation—is configured and launched independently with its own lifecycle manager and parameter file.

## Package Layout

```text
testbed_navigation/
├── CMakeLists.txt
├── package.xml
├── README.md
├── config/
│   ├── map_server_params.yaml   # Static map server parameters
│   ├── amcl_params.yaml         # AMCL localization parameters
│   └── nav2_params.yaml         # Planners, controller, costmaps, behaviors, BT, velocity smoother
├── launch/
│   ├── map_loader.launch.py     # nav2_map_server + lifecycle_manager_map
│   ├── localization.launch.py   # nav2_amcl + lifecycle_manager_localization
│   ├── navigation.launch.py     # Manual Nav2 navigation servers + lifecycle_manager_navigation
│   └── bringup_nav.launch.py    # Convenience wrapper including all three launch files
├── rviz/
│   └── nav2_view.rviz           # RViz2 display config for map, AMCL, costmaps, and paths
└── scripts/
    └── send_goal.py             # CLI action client for sending NavigateToPose goals
```

## Approach & Design Decisions

### 1. Fixing Starter-Code Bugs First
Before writing any Nav2 configuration, I audited the provided packages (`testbed_description`, `testbed_gazebo`, `testbed_bringup`) and fixed the build, map-loading, TF clock, and sensor issues documented in the root [`bugs_and_fixes.txt`](../bugs_and_fixes.txt). The most impactful fixes for navigation were:
- Adding `maps` to `testbed_bringup/CMakeLists.txt` and fixing `image: testbed_world.pgm` in `testbed_world.yaml`.
- Adding `use_sim_time: true` (via `ParameterValue(..., value_type=bool)`) to `robot_state_publisher` so TF frames (`base_footprint -> lidar_link_1`) stay synchronized with Gazebo's `/clock`.
- Increasing the simulated 2D LiDAR max range from `1.5 m` to `12.0 m` so AMCL and costmaps can observe surrounding walls in the playground.
- Raising drive-wheel friction (`mu1/mu2 = 1.0`) and lowering fixed-caster friction (`0.01`) to reduce turning slip.

### 2. Modular Launch & Lifecycle Separation
Each stage uses its own `nav2_lifecycle_manager` instance (`lifecycle_manager_map`, `lifecycle_manager_localization`, `lifecycle_manager_navigation`) and `nav2_common.launch.RewrittenYaml` for clean parameter propagation. This lets each launch file be started, stopped, and debugged in its own terminal without node-name collisions or depending on `nav2_bringup`.

### 3. Robot Frame & Parameter Tuning
From `testbed.xacro` and `testbed.gazebo`:
- **Frames**: `map -> odom -> base_footprint -> base_link -> lidar_link_1`
- **Topics**: `/scan` (`sensor_msgs/LaserScan`), `/odom` (`nav_msgs/Odometry`), `/cmd_vel` (`geometry_msgs/Twist`)
- **Geometry**: Wheel separation `0.35 m`, wheel diameter `0.10 m`, chassis/caster bounding extent ~`0.35 m x 0.39 m` -> configured `robot_radius: 0.25` in both local and global costmaps.
- **Initial Pose**: `spawn_testbed.launch.py` spawns the robot at `(x=0.0, y=5.0, yaw=0.0)`, so `amcl_params.yaml` enables `set_initial_pose: true` at `(0.0, 5.0, 0.0)` while still accepting manual overrides via RViz2's **2D Pose Estimate**.
- **Plugin Selection**:
  - Global planner: `nav2_navfn_planner/NavfnPlanner`
  - Local controller: `dwb_core::DWBLocalPlanner`
  - Path smoother: `nav2_smoother::SimpleSmoother`
  - Recovery behaviors: `nav2_behaviors/{Spin, BackUp, DriveOnHeading, Wait}`
  - Velocity smoothing: `nav2_velocity_smoother` wired via `controller_server -> /cmd_vel_nav -> velocity_smoother -> /cmd_vel` so velocity and acceleration ramps stay smooth on the differential drive base.

## Prerequisites

Install ROS2 Humble Nav2 packages, RViz plugins, and Cyclone DDS (recommended to avoid Fast DDS discovery timeouts):

```bash
sudo apt update
sudo apt install -y   ros-humble-navigation2   ros-humble-nav2-bringup   ros-humble-nav2-rviz-plugins   ros-humble-rmw-cyclonedds-cpp
```

## Build & Run

```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

### Step-by-Step Modular Launch (Recommended)

Open four terminals (source `install/setup.bash` and set `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` in each):

1. **Simulation & Robot Bringup**
   ```bash
   ros2 launch testbed_bringup testbed_full_bringup.launch.py
   ```
2. **Map Server**
   ```bash
   ros2 launch testbed_navigation map_loader.launch.py
   ```
3. **AMCL Localization**
   ```bash
   ros2 launch testbed_navigation localization.launch.py
   ```
   Verify in RViz2 that the `/map` display is visible (Durability Policy: `Transient Local`) and the `/scan` laser points align with the map walls. If needed, refine the pose with **2D Pose Estimate**.
4. **Navigation Stack**
   ```bash
   ros2 launch testbed_navigation navigation.launch.py
   ```
   Send a goal using RViz2's **2D Goal Pose** tool, or from the CLI:
   ```bash
   ros2 run testbed_navigation send_goal.py --x 2.0 --y 3.0 --yaw 0.0
   ```

Alternatively, after starting Terminal 1 (`testbed_full_bringup.launch.py`), you can launch all three navigation stages together with:

```bash
ros2 launch testbed_navigation bringup_nav.launch.py
```

And optionally open the preconfigured Nav2 RViz2 layout:

```bash
rviz2 -d $(ros2 pkg prefix testbed_navigation)/share/testbed_navigation/rviz/nav2_view.rviz
```

## Challenges Faced & Troubleshooting

- **TF Extrapolation Errors**: Without `use_sim_time: true` on `robot_state_publisher`, AMCL and the costmaps reject `/scan` transforms. Checking `ros2 run tf2_tools view_frames` confirmed clean timestamps once `robot_description.launch.py` was updated.
- **Map Not Appearing in RViz2**: `nav2_map_server` publishes `/map` with `Transient Local` durability; RViz2's Map display must match that QoS policy (`Transient Local` / `Reliable`), and Fixed Frame must be set to `map`.
- **Humble Plugin Compatibility**: ROS2 Humble uses `/` separators for `nav2_navfn_planner/NavfnPlanner` and `nav2_behaviors/Spin`, and `bt_navigator` loads its compiled-in default BT libraries when `plugin_lib_names` is left at default—avoiding library-load crashes across Humble patch versions.
- **DDS Timeouts**: Switching to `rmw_cyclonedds_cpp` eliminated intermittent lifecycle transition timeouts between `lifecycle_manager` and Nav2 servers.

## Demo Screenshots / Video

- [Localization & Navigation Demo - Part 1](media/demo_1.mp4)
- [Localization & Navigation Demo - Part 2](media/demo_2.mp4)

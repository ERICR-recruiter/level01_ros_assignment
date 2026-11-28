# Bugs Identified and Fixed (`level01_ros_assignment`)

This report documents every bug and configuration defect identified during the audit of the starter packages (`testbed_description`, `testbed_gazebo`, `testbed_bringup`) and the in-progress `testbed_navigation` package, along with root causes, fixes applied, and verification status.

---

## Starter Repository Bugs

### BUG-01: Malformed XML Closing Tag (`>>`) in IMU Gazebo Plugin
- **File**: `testbed_description/urdf/testbed.gazebo`
- **Root Cause**: Line 40 contained a stray extra `>` character: `<initial_orientation_as_reference>false</initial_orientation_as_reference>>`, injecting invalid stray character data inside the `<plugin>` block when converted to SDF by Gazebo Classic.
- **Fix**: Removed the stray `>` character.
- **Verification**: Static XML parse and stray `>>` scan passed across all 24 XML/Xacro/SDF files.

### BUG-02: Non-Existent ROS 1 Plugin `libgazebo_ros_control.so`
- **File**: `testbed_description/urdf/testbed.gazebo`
- **Root Cause**: The URDF loaded `<plugin name="control" filename="libgazebo_ros_control.so"/>`, which is a ROS 1 plugin that does not exist in ROS 2 Humble (`gazebo_ros_pkgs`). Gazebo Classic 11 fails to load this shared library on startup, while the robot is already controlled by `libgazebo_ros_diff_drive.so`.
- **Fix**: Removed the obsolete `libgazebo_ros_control.so` plugin block.
- **Verification**: Confirmed `libgazebo_ros_control.so` is absent and all three ROS 2 Gazebo plugins (`libgazebo_ros_diff_drive.so`, `libgazebo_ros_ray_sensor.so`, `libgazebo_ros_imu_sensor.so`) are present.

### BUG-03: Severely Truncated LiDAR Maximum Range (`1.5 m`)
- **File**: `testbed_description/urdf/testbed.gazebo`
- **Root Cause**: The ray sensor `<range><max>` was set to `1.5` meters inside a 20 m × 20 m world (`testbed_playground.world`). At the default spawn location `(0.0, 5.0)`, surrounding walls are ~4–5 m away, leaving the robot effectively blind to map walls and preventing AMCL from converging.
- **Fix**: Upgraded LiDAR `<max>` range to `12.0` m, `<min>` to `0.15` m (clearing the 9 cm LiDAR housing), `<samples>` to `360`, angular span to `[-3.14159, 3.14159]`, and `<update_rate>` to `10` Hz (reducing simulation CPU load and preventing scan queue drops).
- **Verification**: Verified in `testbed.gazebo` and synchronized with `amcl_params.yaml` (`laser_max_range: 12.0`, `laser_min_range: 0.15`) and costmap `obstacle_layer` ranges (`obstacle_max_range: 4.5`, `raytrace_max_range: 5.5`).

### BUG-04: Inaccurate Wheel Separation (`0.35 m` vs. `0.376 m`) and Slippery Wheel / Sticky Caster Friction
- **File**: `testbed_description/urdf/testbed.gazebo`
- **Root Cause**:
  1. Direct STL mesh and URDF joint measurement shows `left_wheel_1.stl` centered at `Y = +0.1502 m` and `right_wheel_1.stl` centered at `Y = -0.2258 m`, giving a true center-to-center wheel separation of **0.376 m** (not `0.35 m`, a ~7% yaw odometry error during rotation). Wheel diameter was verified as `0.100 m`.
  2. Drive wheels (`left_wheel_1`, `right_wheel_1`) and fixed non-rotating casters (`caster_1`..`caster_4`) all had identical friction (`mu1=0.2, mu2=0.2`), causing severe drive-wheel slip and caster drag during turns.
  3. `libgazebo_ros_diff_drive.so` omitted explicit `<max_wheel_torque>` and `<max_wheel_acceleration>` limits.
- **Fix**: Updated `<wheel_separation>` to `0.376`, added `<max_wheel_torque>20</max_wheel_torque>` and `<max_wheel_acceleration>1.0</max_wheel_acceleration>`, set drive wheel friction to `mu1=1.0, mu2=1.0`, set fixed caster friction to `mu1=0.01, mu2=0.01`, and set `<self_collide>false</self_collide>` on chassis/wheel/caster links to avoid internal mesh contact jitter.
- **Verification**: Verified mathematically against binary STL vertex bounds and validated in `testbed.gazebo`.

### BUG-05: Missing `use_sim_time` and Unsafe `robot_description` Parameter Type in `robot_description.launch.py`
- **File**: `testbed_description/launch/robot_description.launch.py`
- **Root Cause**: `robot_state_publisher` was launched without `use_sim_time: true`, causing it to stamp static/robot transforms with wall-clock time while Gazebo stamped `/odom` and `/scan` with simulation time (`/clock`), producing TF extrapolation errors in RViz2 and Nav2. Additionally, raw `Command(...)` output was not wrapped in `ParameterValue(..., value_type=str)`.
- **Fix**: Added a `use_sim_time` launch argument (default `'true'`), wrapped both `robot_description` (`str`) and `use_sim_time` (`bool`) with `ParameterValue`.
- **Verification**: Python `py_compile` and AST check passed.

### BUG-06: Zero-Dimension Visual Box on `base_footprint`
- **File**: `testbed_description/urdf/testbed.xacro`
- **Root Cause**: `<link name="base_footprint">` contained a `<visual>` with `<box size="0.0 0.0 0.0" />`, which triggers zero-dimension geometry warnings in Gazebo Classic.
- **Fix**: Simplified to `<link name="base_footprint"/>`.
- **Verification**: URDF XML parse and kinematic tree root check passed.

### BUG-07: `models/` Directory Not Installed in `testbed_gazebo/CMakeLists.txt`
- **File**: `testbed_gazebo/CMakeLists.txt`
- **Root Cause**: `install(DIRECTORY launch worlds ...)` omitted the `models` directory even though `spawn_playground.launch.py` adds `share/testbed_gazebo/models` to `GAZEBO_MODEL_PATH`.
- **Fix**: Added `models` to the `install(DIRECTORY launch worlds models ...)` directive.
- **Verification**: Inspected `CMakeLists.txt` and confirmed `testbed_gazebo/models/` exists.

### BUG-08: `world` Launch Argument Not Explicitly Forwarded to `gazebo.launch.py`
- **File**: `testbed_gazebo/launch/spawn_playground.launch.py`
- **Root Cause**: `IncludeLaunchDescription` for `gazebo_ros/launch/gazebo.launch.py` did not pass `launch_arguments={'world': LaunchConfiguration('world')}`, and `default_value` used a list with a trailing empty string.
- **Fix**: Explicitly passed `world` and `verbose` via `launch_arguments` and simplified `default_value` to a clean path string.
- **Verification**: Python `py_compile` and AST check passed.

### BUG-09: Gazebo Startup / Entity Spawn Race Condition & Hardcoded Spawn Pose
- **Files**: `testbed_bringup/launch/testbed_full_bringup.launch.py`, `testbed_gazebo/launch/spawn_testbed.launch.py`
- **Root Cause**: `testbed_full_bringup.launch.py` launched `spawn_testbed.launch.py` simultaneously with `gazebo.launch.py` without waiting for `/spawn_entity` to become available, did not propagate `use_sim_time` to `robot_description.launch.py`, and spawned at `z=0.0` without spawn timeout or configurable pose arguments.
- **Fix**: Wrapped `spawn_testbed.launch.py` in `TimerAction(period=3.0)`, propagated `use_sim_time`, added `use_rviz` toggle, parameterized `x_pose`, `y_pose`, `z_pose` (`0.01` m clearance), and `yaw` in `spawn_testbed.launch.py`, and added `-timeout 60` to `spawn_entity.py`.
- **Verification**: Verified spawn point `(0.0, 5.0)` is in collision-free space (`pixel=254`) on `testbed_world.pgm`; Python syntax/AST checks passed.

### BUG-10: Missing Package Dependencies Across Starter Packages
- **Files**: `testbed_description/package.xml`, `testbed_gazebo/package.xml`, `testbed_bringup/package.xml`, `testbed_bringup/CMakeLists.txt`
- **Root Cause**: Runtime dependencies (`xacro`, `robot_state_publisher`, `joint_state_publisher`, `rviz2`, `gazebo_ros`, `gazebo_plugins`, `testbed_description`, `testbed_gazebo`, `launch`, `launch_ros`) were missing from `package.xml` files, while `testbed_bringup/CMakeLists.txt` called `find_package(rclpy REQUIRED)` without declaring `rclpy` in `package.xml` or using it.
- **Fix**: Added complete `<exec_depend>` entries in all three `package.xml` files and removed unused `find_package(rclpy REQUIRED)` from `testbed_bringup/CMakeLists.txt`.
- **Verification**: Validated all `package.xml` files with XML parser.

### BUG-11: Hardcoded Local Author Path in `.vscode/settings.json`
- **File**: `.vscode/settings.json`
- **Root Cause**: Contained `"/home/eric-ros1/level01_ros_assignment/testbed_bringup"`.
- **Fix**: Replaced with `"${workspaceFolder}/testbed_bringup"`.
- **Verification**: Confirmed clean portable path.

---

## `testbed_navigation` Package Bugs & Upgrades

### BUG-12: Missing Required `testbed_navigation/config/amcl_params.yaml`
- **Files**: `testbed_navigation/config/amcl_params.yaml`, `testbed_navigation/launch/localization.launch.py`
- **Root Cause**: Assignment Section 5 explicitly requires AMCL parameters in `testbed_navigation/config/amcl_params.yaml`. Previously, AMCL parameters were bundled into `nav2_params.yaml` and `amcl_params.yaml` did not exist.
- **Fix**: Created dedicated `config/amcl_params.yaml` (and `config/map_server_params.yaml`) and updated `localization.launch.py` to load `amcl_params.yaml` by default.
- **Verification**: YAML parse and AMCL schema check passed.

### BUG-13: Empty and Misplaced `BUGS_FIXED.txt`
- **Files**: `testbed_navigation/BUGS_FIXED.txt` (removed), `BUGS_FIXED.txt` & `BUGS_FIXED.md` (root directory)
- **Root Cause**: The original assignment instructs placing the bug-fix text file in the root directory outside `testbed_navigation`. Previously, an empty 0-byte `BUGS_FIXED.txt` sat inside `testbed_navigation/`.
- **Fix**: Removed the empty file and its `CMakeLists.txt` install rule; added complete `BUGS_FIXED.md` and `BUGS_FIXED.txt` at the repository root.
- **Verification**: Verified non-empty root files and clean `testbed_navigation/CMakeLists.txt`.

### BUG-14: Missing ROS 2 Humble `plugin_lib_names` in `bt_navigator`
- **File**: `testbed_navigation/config/nav2_params.yaml`
- **Root Cause**: `bt_navigator` did not declare `plugin_lib_names` for ROS 2 Humble Behavior Tree nodes.
- **Fix**: Added the complete, verified ROS 2 Humble `plugin_lib_names` list (47 standard Nav2 Humble BT plugin libraries).
- **Verification**: YAML parse and schema validation confirmed 47 Humble BT libraries present.

### BUG-15: Undersized Provisional `robot_radius: 0.20` vs. Actual Asymmetric Robot Geometry
- **File**: `testbed_navigation/config/nav2_params.yaml`
- **Root Cause**: Both costmaps used a provisional `robot_radius: 0.20` m. STL mesh inspection revealed the chassis + wheels span `X in [-0.226, +0.124] m` and `Y in [-0.241, +0.165] m` (circumradius `0.330 m`), meaning `0.20 m` risked wall collisions on the rear and right side.
- **Fix**: Replaced provisional `robot_radius` with the exact measured polygon `footprint: "[[-0.24, -0.25], [-0.24, 0.18], [0.14, 0.18], [0.14, -0.25]]"` (includes 2 cm margin) and set `inflation_radius: 0.45` m (`cost_scaling_factor: 3.0`) to clear 0.90 m doorways safely.
- **Verification**: Verified against STL mesh bounds and `testbed_playground.world` doorway widths (0.90 m).

### BUG-16: Outdated Costmap LiDAR Ranges & Overly Tight Local Costmap Window
- **File**: `testbed_navigation/config/nav2_params.yaml`
- **Root Cause**: Costmap `obstacle_max_range` (`1.40 m`) and `raytrace_max_range` (`1.50 m`) matched the broken 1.5 m LiDAR, and `local_costmap` was only `3x3 m`.
- **Fix**: Updated `obstacle_max_range: 4.5`, `raytrace_max_range: 5.5`, `obstacle_min_range: 0.15`, `raytrace_min_range: 0.15`, and expanded `local_costmap` to `4x4 m`.
- **Verification**: Validated in YAML schema check.

### BUG-17: Missing `nav2_smoother`, `testbed_bringup`, and `rviz2` Dependencies in `testbed_navigation/package.xml`
- **File**: `testbed_navigation/package.xml`
- **Root Cause**: `navigation.launch.py` launched `nav2_smoother` and `map_loader.launch.py` queried `testbed_bringup`, but neither was listed in `package.xml`.
- **Fix**: Added `nav2_smoother`, `testbed_bringup`, and `rviz2` as `<exec_depend>` entries.
- **Verification**: XML validation passed.

### BUG-18: Missing Nav2-Ready RViz2 Configuration & Staged Bringup Launcher
- **Files**: `testbed_navigation/rviz/nav2_view.rviz`, `testbed_navigation/launch/bringup_navigation.launch.py`, `testbed_navigation/CMakeLists.txt`
- **Root Cause**: `testbed_description/rviz/full_bringup.rviz` used Fixed Frame `odom` and lacked Map, AMCL Particles, Global/Local Costmaps, Global/Local Paths, and Robot Footprint displays.
- **Fix**: Added `testbed_navigation/rviz/nav2_view.rviz`, installed `rviz` in `CMakeLists.txt`, and added `bringup_navigation.launch.py` as a staged convenience launcher alongside the three required independent launch files.
- **Verification**: YAML parse of `nav2_view.rviz` and Python compile/AST check of `bringup_navigation.launch.py` passed.

---

## Independent Review Follow-up (2026-11-28)

### REVIEW-01: Explicit ROS 2 Gazebo plugin search path
- **File**: `testbed_gazebo/launch/spawn_playground.launch.py`
- **Finding**: The launch file previously appended only the `testbed_description` package's `lib` directory to `GAZEBO_PLUGIN_PATH`. The ROS 2 Gazebo plugins used by this project are installed under the ROS distribution prefix's `lib` directory (normally `/opt/ros/humble/lib`). If that path is absent from the Gazebo process environment, Gazebo Classic can fail to load `libgazebo_ros_init.so`, `libgazebo_ros_factory.so`, and `libgazebo_ros_diff_drive.so`, leaving `/spawn_entity`, `/odom`, or drive command integration unavailable.
- **Change**: Resolve the `gazebo_ros` package prefix at launch time and append `<gazebo_ros-prefix>/lib` plus the project description package's `lib` path to `GAZEBO_PLUGIN_PATH`, preserving pre-existing entries and avoiding duplicates.
- **Verification status**: Static Python syntax validation passed. This environment does not contain ROS 2 Humble or Gazebo Classic, so live plugin loading and `/odom` publication remain **unverified** and must be checked on the target Ubuntu machine.

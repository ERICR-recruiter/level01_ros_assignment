# Bugs Identified and Fixed in Starter Code

**Candidate:** MD Akmal  
**Role:** ROS Intern - ERIC Robotics  
**Target Platform:** ROS 2 Humble / Gazebo Classic 11 / Ubuntu 22.04  

---

## Overview

A total of **11 issues and intentional bugs** were identified and corrected in the starter codebase. Below is the detailed breakdown of each bug, its root cause, and the applied solution.

---

### 1. Build Failure: Missing Parentheses in `ament_package` Macro
- **File:** [`testbed_description/CMakeLists.txt`](testbed_description/CMakeLists.txt#L23)
- **Problem:** The file ended with bare `ament_package` without parentheses `()`.
- **Root Cause:** CMake requires parentheses for macro/function invocation. Without them, CMake parser halts with `Parse error. Expected "(", got newline`.
- **Fix:** Changed to `ament_package()`.
- **Verification:** Workspace builds without CMake parsing errors.

---

### 2. Map Server Crash: Incorrect Map Image Filename in YAML
- **File:** [`testbed_bringup/maps/testbed_world.yaml`](testbed_bringup/maps/testbed_world.yaml#L1)
- **Problem:** `image:` field referenced `wrong_path_testbed_world.pgm`.
- **Root Cause:** The actual occupancy grid image is `testbed_world.pgm`. When `nav2_map_server` attempted to load the file, it threw a `No such file or directory` exception and crashed the lifecycle node.
- **Fix:** Updated line 1 to `image: testbed_world.pgm`.
- **Verification:** `map_server` successfully transitions to `active` and publishes the 405x400 occupancy grid on `/map`.

---

### 3. Missing Runtime Files: `maps` Directory Omitted from Installation
- **File:** [`testbed_bringup/CMakeLists.txt`](testbed_bringup/CMakeLists.txt#L27-L32)
- **Problem:** `install(DIRECTORY ...)` only copied the `launch/` directory.
- **Root Cause:** The `maps/` directory containing the map YAML and PGM was not installed into `install/testbed_bringup/share/testbed_bringup/maps/`. Launch files resolving the map path via `get_package_share_directory('testbed_bringup')` failed at runtime.
- **Fix:** Added `maps` to `install(DIRECTORY launch maps DESTINATION share/${PROJECT_NAME}/)`.
- **Verification:** Map files are correctly placed in the package share directory.

---

### 4. Missing Simulation Models: `models` Directory Omitted from Installation
- **File:** [`testbed_gazebo/CMakeLists.txt`](testbed_gazebo/CMakeLists.txt#L28-L34)
- **Problem:** `install(DIRECTORY ...)` only installed `launch` and `worlds`, omitting `models`.
- **Root Cause:** `spawn_playground.launch.py` adds `share/testbed_gazebo/models` to `GAZEBO_MODEL_PATH`. Without installing `models`, custom Gazebo entities (`test_room`, `wooden_fence`, `box_room`) failed to resolve.
- **Fix:** Added `models` to `install(DIRECTORY launch worlds models DESTINATION share/${PROJECT_NAME}/)`.
- **Verification:** Verified all model SDFs, materials, and meshes exist in the install directory.

---

### 5. XML Parser Syntax Error: Stray Character in Gazebo IMU Sensor Tag
- **File:** [`testbed_description/urdf/testbed.gazebo`](testbed_description/urdf/testbed.gazebo#L40)
- **Problem:** Tag had double closing angle brackets: `</initial_orientation_as_reference>>`.
- **Root Cause:** The second `>` is parsed as invalid loose text inside the plugin element, causing `xacro` and Gazebo SDF converters to fail.
- **Fix:** Removed the stray `>` character.
- **Verification:** `xacro` compiles URDF without XML parsing exceptions.

---

### 6. Incompatible Legacy ROS 1 Plugin in Gazebo Description
- **File:** [`testbed_description/urdf/testbed.gazebo`](testbed_description/urdf/testbed.gazebo#L7)
- **Problem:** Loaded ROS 1 plugin `<plugin name="control" filename="libgazebo_ros_control.so"/>`.
- **Root Cause:** `libgazebo_ros_control.so` does not exist in ROS 2 Humble. Attempting to load it outputs fatal plugin errors at entity spawn time. Furthermore, the robot is actuated via `libgazebo_ros_diff_drive.so`, making the control plugin redundant.
- **Fix:** Removed the legacy plugin declaration.
- **Verification:** Clean Gazebo entity spawning with zero plugin load errors.

---

### 7. Lidar Max Range Inadequate for Localization and Costmaps
- **File:** [`testbed_description/urdf/testbed.gazebo`](testbed_description/urdf/testbed.gazebo#L65)
- **Problem:** Lidar ray range `<max>` was set to `1.5` meters.
- **Root Cause:** The test arena is ~20m x 20m. With a 1.5m range, the robot cannot see walls or obstacles in open areas. AMCL likelihood-field particle filtering cannot converge, and Nav2 costmaps fail to detect obstacles ahead of time.
- **Fix:** Increased `<max>` to `12.0` meters and matched AMCL `laser_max_range: 12.0` and costmap raytrace ranges.
- **Verification:** LaserScan covers arena geometry; AMCL particle cloud converges upon receiving scans.

---

### 8. Wheel and Caster Friction Discrepancy Causing Slip and Stalling
- **File:** [`testbed_description/urdf/testbed.gazebo`](testbed_description/urdf/testbed.gazebo#L98-L158)
- **Problem:** Passive casters and drive wheels both had friction coefficients `mu1 = 0.2`, `mu2 = 0.2`.
- **Root Cause:** In differential drive robots with passive casters, casters must have low friction (`~0.001`) to allow smooth omnidirectional sliding. Having `mu1 = 0.2` across four casters creates excessive lateral drag that the drive wheels cannot overcome, leading to stalled motion or erratic wheel slipping.
- **Fix:**
  - Casters (`caster_1` to `caster_4`): Set `mu1 = 0.001`, `mu2 = 0.001`.
  - Drive wheels (`left_wheel_1`, `right_wheel_1`): Set `mu1 = 1.0`, `mu2 = 1.0`.
- **Verification:** Robot drives smoothly along commanded velocities without stalling.

---

### 9. Simulation Clock Desynchronization in `robot_state_publisher`
- **File:** [`testbed_description/launch/robot_description.launch.py`](testbed_description/launch/robot_description.launch.py)
- **Problem:** `robot_state_publisher` was started without `use_sim_time: True`.
- **Root Cause:** Gazebo publishes timestamps on `/clock`. Without simulation time enabled, `robot_state_publisher` uses system wall-clock time, creating a time offset between TF frames and incoming sensor/odom messages. Nav2 throws TF extrapolation errors.
- **Fix:** Added `use_sim_time: True` and wrapped the xacro Command with `ParameterValue(..., value_type=str)`.
- **Verification:** Synchronous TF transforms across `map`, `odom`, and `base_footprint`.

---

### 10. Blank Robot Rendering in RViz Due to Volatile QoS
- **File:** [`testbed_description/rviz/full_bringup.rviz`](testbed_description/rviz/full_bringup.rviz#L61)
- **Problem:** RobotModel display durability policy was set to `Volatile`.
- **Root Cause:** In ROS 2, `robot_state_publisher` publishes the `/robot_description` topic with `Transient Local` durability. When RViz starts after `robot_state_publisher`, a `Volatile` subscriber misses the latched message and the robot model remains blank.
- **Fix:** Updated Durability Policy from `Volatile` to `Transient Local`.
- **Verification:** Robot 3D model renders immediately when RViz starts.

---

### 11. Missing Package Dependencies in `package.xml`
- **Files:** `testbed_bringup/package.xml`, `testbed_description/package.xml`, `testbed_gazebo/package.xml`
- **Problem:** Launch files relied on `xacro`, `robot_state_publisher`, `joint_state_publisher`, `gazebo_ros`, and `rviz2`, but these were not declared as runtime dependencies.
- **Fix:** Added `<exec_depend>` declarations across all `package.xml` files.
- **Verification:** Clean `rosdep install` validation.

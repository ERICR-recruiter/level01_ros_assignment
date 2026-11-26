# BUG_FIXES.md — Testbed-T1.0.0 Starter Repository Bug Report

**Author**: Kunal J  
**Date**: 2026-11-24  
**Repository**: ERIC-L1-ROS-assignment  
**Robot**: Testbed-T1.0.0  
**Target Platform**: ROS 2 Humble / Ubuntu 22.04 / Gazebo Classic 11  

---

## A. Confirmed Bugs Fixed

### BUG 1: CMake `ament_package` missing parentheses

| Field | Detail |
|---|---|
| **File** | `testbed_description/CMakeLists.txt` (line 23) |
| **Original issue** | `ament_package` written without parentheses |
| **Technical explanation** | `ament_package` is a CMake macro. Without `()`, CMake treats it as a variable reference rather than a macro invocation. The macro is never called, so the package's ament index entry, package marker, and CMake config files are never generated. |
| **Root cause** | Typographic error — missing `()` |
| **Before** | `ament_package` |
| **After** | `ament_package()` |
| **Verification** | `colcon build --packages-select testbed_description` completes without CMake errors; the ament index entry is created in the install directory. |
| **Validation result** | Static validation passed — CMake syntax is correct. Runtime build validation requires Ubuntu/ROS 2 environment. |

---

### BUG 2: Map YAML references non-existent image file

| Field | Detail |
|---|---|
| **File** | `testbed_bringup/maps/testbed_world.yaml` (line 1) |
| **Original issue** | `image: wrong_path_testbed_world.pgm` — file does not exist |
| **Technical explanation** | The map YAML is consumed by `nav2_map_server`. The `image` field must reference the actual PGM occupancy grid file. The file `wrong_path_testbed_world.pgm` does not exist in the `maps/` directory; the actual file is `testbed_world.pgm`. |
| **Root cause** | Intentional bug — `wrong_path_` prefix prepended to the filename |
| **Before** | `image: wrong_path_testbed_world.pgm` |
| **After** | `image: testbed_world.pgm` |
| **Verification** | `python3 -c "import yaml; print(yaml.safe_load(open('testbed_bringup/maps/testbed_world.yaml')))"` confirms valid YAML; `ls testbed_bringup/maps/testbed_world.pgm` confirms PGM exists (162,015 bytes, 405×400 pixels). |
| **Validation result** | ✅ YAML parses correctly. PGM file exists and matches (405×400 px, 162,015 bytes). |

---

### BUG 3: IMU plugin XML syntax error — stray `>` and tag misplacement

| Field | Detail |
|---|---|
| **File** | `testbed_description/urdf/testbed.gazebo` (original line 40) |
| **Original issue** | `<initial_orientation_as_reference>false</initial_orientation_as_reference>>` — (1) stray `>` after closing tag, (2) tag placed outside `<plugin>` block (between `<plugin ...>` and `<ros>`) with incorrect indentation |
| **Technical explanation** | The extra `>` creates malformed XML. Additionally, `<initial_orientation_as_reference>` is a parameter of the `gazebo_ros_imu_sensor` plugin and must be a child element inside the `<plugin>` block. Being placed before the `<plugin>` proper child content (and after the opening `<plugin>` tag but with wrong nesting) violates the expected schema. |
| **Root cause** | Typographic/editing error — stray character and incorrect tag placement |
| **Before** | `<plugin name="my_imu_plugin" filename="libgazebo_ros_imu_sensor.so">` followed by `<initial_orientation_as_reference>false</initial_orientation_as_reference>>` (note: stray `>`, outside proper indentation) |
| **After** | `<initial_orientation_as_reference>` moved inside `<plugin>` block with correct indentation and stray `>` removed |
| **Verification** | `python3 -c "import xml.etree.ElementTree as ET; ET.parse('testbed_description/urdf/testbed.gazebo'); print('VALID')"` returns VALID. The generated URDF via xacro should contain the corrected IMU plugin configuration. |
| **Validation result** | ✅ XML validates successfully with Python ElementTree parser. |

---

### BUG 4: `maps/` directory not installed in testbed_bringup

| Field | Detail |
|---|---|
| **File** | `testbed_bringup/CMakeLists.txt` (line 27-32) |
| **Original issue** | Only `launch` directory is installed; `maps` is missing from the `install(DIRECTORY ...)` directive |
| **Technical explanation** | After `colcon build`, the `maps/` directory (containing `testbed_world.yaml` and `testbed_world.pgm`) is not copied to the install space. Any code that uses `get_package_share_directory('testbed_bringup') + '/maps/...'` to find the map files will fail with a file-not-found error at runtime. |
| **Root cause** | Omission — `maps` directory not included in install target |
| **Before** | `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)` |
| **After** | `install(DIRECTORY launch maps DESTINATION share/${PROJECT_NAME}/)` |
| **Verification** | After `colcon build`, verify `ls $(ros2 pkg prefix testbed_bringup)/share/testbed_bringup/maps/` contains both `testbed_world.yaml` and `testbed_world.pgm`. |
| **Validation result** | Static validation passed — CMake syntax is correct. Runtime installation verification requires build environment. |

---

### BUG 5: Obsolete ROS 1 Gazebo control plugin

| Field | Detail |
|---|---|
| **File** | `testbed_description/urdf/testbed.gazebo` (original lines 6-8) |
| **Original issue** | `<plugin name="control" filename="libgazebo_ros_control.so"/>` — this is a ROS 1 Gazebo plugin |
| **Technical explanation** | `libgazebo_ros_control.so` is from the ROS 1 `gazebo_ros_control` package. It does not exist in ROS 2 Humble. The ROS 2 equivalent is `libgazebo_ros2_control.so` from `gazebo_ros2_control`, but this robot uses the `libgazebo_ros_diff_drive.so` plugin for motor control, making any separate control plugin unnecessary. Loading a non-existent library causes Gazebo to emit errors during model loading. |
| **Root cause** | Legacy ROS 1 artifact left in the robot description |
| **Before** | `<gazebo><plugin name="control" filename="libgazebo_ros_control.so"/></gazebo>` |
| **After** | Entire `<gazebo>` block containing this plugin removed |
| **Verification** | Spawn robot in Gazebo; confirm no `libgazebo_ros_control.so` load errors; confirm differential-drive plugin loads and publishes `/odom` and subscribes to `/cmd_vel`. |
| **Validation result** | ✅ XML validates. Plugin block cleanly removed. Diff-drive plugin retained intact. |

---

### BUG 6: Differential-drive wheel separation mismatch with URDF geometry

| Field | Detail |
|---|---|
| **File** | `testbed_description/urdf/testbed.gazebo` (original line 17) |
| **Original issue** | `<wheel_separation>0.35</wheel_separation>` does not match the URDF joint geometry |
| **Technical explanation** | The wheel separation in a differential-drive controller must match the actual distance between wheel contact patches. From the URDF: left_wheel_joint Y = +0.135241 m, right_wheel_joint Y = −0.210759 m. Geometric separation = \|0.135241 − (−0.210759)\| = **0.346 m**. The configured value of 0.35 m introduces a 1.16% error. This causes 4.2° of cumulative heading drift per full revolution, which significantly degrades AMCL localization and Nav2 path tracking. |
| **Root cause** | Incorrect parameter value — does not match URDF geometry |
| **Calculation** | `abs(0.135241 - (-0.210759)) = abs(0.135241 + 0.210759) = 0.346000 m` |
| **Before** | `<wheel_separation>0.35</wheel_separation>` |
| **After** | `<wheel_separation>0.346</wheel_separation>` |
| **Verification** | Command `ros2 topic pub /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.2}}'` and verify robot drives straight. For rotational test: command pure rotation and verify odometry reports correct angular displacement. |
| **Validation result** | Geometric calculation verified with diagnostic script. Runtime validation requires Gazebo simulation environment. |

---

## B. Investigated Issues That Did Not Require Modification

### ISSUE A: Robot Spawn Position — VALID, NOT MODIFIED

| Field | Detail |
|---|---|
| **File** | `testbed_gazebo/launch/spawn_testbed.launch.py` (line 15) |
| **Reported concern** | Robot spawns at `position = [0.0, 5.0, 0.0]`, which may be outside the navigable area |
| **Investigation method** | Python diagnostic script analyzed the PGM occupancy grid (405×400 px, resolution 0.05 m/px, origin [-10.2, -9.94, 0]). The robot footprint (0.44×0.44 m = 9×9 pixel kernel) was tested at the spawn position. |
| **Findings** | Map world extents: X=[−10.20, 10.05], Y=[−9.94, 10.06]. At spawn (0.0, 5.0), pixel (203, 101): center pixel value = 254/255 (normalized 0.996 > free_thresh 0.25). **All 81 pixels (9×9 footprint) are free space.** Zero occupied or out-of-bounds pixels. |
| **Decision** | **Position is valid.** The robot spawns in confirmed free space within the map boundaries. No modification required. |
| **Evidence** | Diagnostic script output: `RESULT: SAFE — all pixels free` |

---

## C. ROS 2 Compatibility Improvements

### IMPROVEMENT 1: `use_sim_time` parameter added to robot_state_publisher

| Field | Detail |
|---|---|
| **File** | `testbed_description/launch/robot_description.launch.py` (line 26) |
| **Issue** | `robot_state_publisher` node did not set `use_sim_time: True`. When running under Gazebo simulation, all ROS 2 nodes must use simulation time from the `/clock` topic. Without this, TF transforms published by RSP use wall-clock time while Gazebo publishes simulation time, causing TF extrapolation errors in RViz, Nav2, and AMCL. |
| **Context** | The other launch file (`testbed_rviz_barebones.launch.py`) already sets `use_sim_time: True` for its RSP node. The bringup launch file (`testbed_full_bringup.launch.py`) includes `robot_description.launch.py`, inheriting the problem. |
| **Before** | `parameters=[robot_description]` |
| **After** | `parameters=[robot_description, {'use_sim_time': True}]` |
| **Verification** | Launch simulation, then `ros2 param get /robot_state_publisher use_sim_time` returns `True`. TF frames from RSP use Gazebo `/clock` timestamps. |

---

### IMPROVEMENT 2: Missing runtime dependencies added to package.xml files

#### testbed_description/package.xml
| Dependency | Type | Justification |
|---|---|---|
| `xacro` | `<depend>` | URDF is in xacro format; required by all launch files that process the robot description |
| `robot_state_publisher` | `<exec_depend>` | Used in `robot_description.launch.py` and `testbed_rviz_barebones.launch.py` |
| `joint_state_publisher` | `<exec_depend>` | Used in `testbed_rviz_barebones.launch.py` |
| `rviz2` | `<exec_depend>` | Used in `testbed_rviz_barebones.launch.py` |

#### testbed_gazebo/package.xml
| Dependency | Type | Justification |
|---|---|---|
| `gazebo_ros` | `<exec_depend>` | Used in `spawn_playground.launch.py` (via `get_package_share_directory('gazebo_ros')`) and `spawn_testbed.launch.py` (via `gazebo_ros/spawn_entity.py`) |
| `gazebo_ros_pkgs` | `<exec_depend>` | Meta-package providing Gazebo Classic ROS 2 integration plugins (`libgazebo_ros_diff_drive.so`, `libgazebo_ros_ray_sensor.so`, `libgazebo_ros_imu_sensor.so`) |

#### testbed_bringup/package.xml
| Dependency | Type | Justification |
|---|---|---|
| `testbed_description` | `<exec_depend>` | Included via launch file |
| `testbed_gazebo` | `<exec_depend>` | Included via launch file |
| `launch` | `<exec_depend>` | Required by launch system |
| `launch_ros` | `<exec_depend>` | Required for `Node` actions in launch files |
| `rviz2` | `<exec_depend>` | RViz node launched in `testbed_full_bringup.launch.py` |

---

## Validation Summary

| Check | Method | Result |
|---|---|---|
| XML syntax — `testbed.gazebo` | Python `xml.etree.ElementTree.parse()` | ✅ VALID |
| XML syntax — `testbed.xacro` | Python `xml.etree.ElementTree.parse()` | ✅ VALID |
| XML syntax — `testbed.trans` | Python `xml.etree.ElementTree.parse()` | ✅ VALID |
| XML syntax — `materials.xacro` | Python `xml.etree.ElementTree.parse()` | ✅ VALID |
| XML syntax — all `package.xml` files | Python `xml.etree.ElementTree.parse()` | ✅ VALID |
| Python syntax — all launch files | `python3 -m py_compile` | ✅ VALID |
| Map YAML syntax | Python `yaml.safe_load()` | ✅ VALID |
| Map PGM existence | `os.path.exists()` | ✅ EXISTS (162,015 bytes) |
| Map PGM dimensions | PGM parser | ✅ 405×400 pixels |
| Spawn position free-space check | Custom diagnostic script | ✅ SAFE (81/81 pixels free) |
| Wheel separation calculation | Geometric analysis from URDF | ✅ Corrected: 0.35 → 0.346 m |
| Colcon build | Requires Ubuntu/ROS 2 environment | ⏳ Not tested (Windows development host) |
| Gazebo simulation launch | Requires Ubuntu/Gazebo environment | ⏳ Not tested (Windows development host) |
| ROS 2 topic verification | Requires running simulation | ⏳ Not tested (Windows development host) |
| TF tree verification | Requires running simulation | ⏳ Not tested (Windows development host) |

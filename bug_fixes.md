# Bug Fixes & ROS 2 Humble → Jazzy Migration

Changes made to move the testbed from ROS 2 Humble to **Jazzy** (Gazebo Sim), and the bugs fixed along the way.

## 1. Migration from Humble to Jazzy

## 2. `ament_package` missing parentheses
**File:** `testbed_description/CMakeLists.txt`
- **Problem:** `colcon build` failed because the macro was written as `ament_package`.
- **Fix:** `ament_package()`

## 3. Wrong map image path
**File:** `testbed_bringup/maps/testbed_world.yaml`
- **Problem:** `image: wrong_path_testbed_world.pgm` pointed to a nonexistent file, so the map server could not load the map.
- **Fix:** `image: testbed_world.pgm`, and `testbed_bringup` now installs its `maps` directory.

## 4. RViz config path
**File:** `testbed_bringup/launch/testbed_full_bringup.launch.py`
- **Problem:** The RViz config path was built with `launch_ros.substitutions.FindPackageShare(...).find(...)`, so RViz did not load `full_bringup.rviz`.
- **Fix:** Get the package path with `get_package_share_directory('testbed_description')` and join it with `rviz` and `full_bringup.rviz` using `os.path.join`.

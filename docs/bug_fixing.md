# Repository Bug Fixes & Resolved Issues

This document tracks all bugs, syntax errors, and build issues resolved in [`SubhamC07/level01_ros_assignment`](http://github.com/SubhamC07/level01_ros_assignment).

---

## 1. Syntax Error in `testbed_description/CMakeLists.txt`

### **Issue**
Building the `testbed_description` package fails during the CMake configuration step due to a syntax error on the final line of `CMakeLists.txt`.

* **Error Message / Cause:** CMake syntax error caused by missing function invocation parentheses on `ament_package`.

### **Root Cause**
The macros/functions in CMake require parentheses even if no arguments are passed. The file ended with:
`ament_package`

### **Fix**
Updated the last line of `testbed_description/CMakeLists.txt` to properly invoke the `ament_package()` function: `ament_package` to `ament_package()`

## 2. Migration to Ignition Gazebo Fortress

### Issue
Launching the ROS 2 launch file fails at execution time with an AttributeError or failure during launch description generation when resolving rviz_config_dir.

### Error Message / Cause: 
Calling .find('testbed_description') on launch_ros.substitutions.FindPackageShare is invalid Python because substitution objects do not expose a .find() method.

## 3. Setup Launch files for Localization and Navigation

Successfully integrated the AMCL and Nav2 launch sequences to enable full autonomous navigation capabilities within the Ignition Gazebo Fortress environment. This involved configuring custom launch files that sequentially bring up the map server, initialize AMCL for probabilistic robot localization, and start the Nav2 behavior tree, planner, and controller servers. Necessary remappings and frame IDs (map --> odom -->base_link) were established to ensure stable tf2 transforms during simulation.

## 4. Tuning of the Config files

To optimize the robot's navigation performance and ensure smooth path tracking in the simulated environment, several core parameters within the Nav2 configuration YAML files were refined.




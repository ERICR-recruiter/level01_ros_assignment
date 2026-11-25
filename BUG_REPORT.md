# Bug Report – ROS 2 AMR Simulation and Navigation

## 1. Overview

During the development and testing of the AMR simulation, a few issues were identified in the robot description, Gazebo integration, workspace configuration, and Nav2 setup.

These issues affected the robot's TF tree, joint state publishing, package compilation, and navigation visualization. The following report records the problems encountered and the changes made to address them.

## 2. Issues Identified and Fixed

### Bug 1: Missing Joint State Publisher for Wheel Joints

**Area:** Robot Description / Gazebo Integration

**Problem:**

While checking the robot's TF tree, the wheel joint transforms were not being published through the expected joint-state pipeline. On investigation, `/joint_states` had no active publisher, even though `robot_state_publisher` was subscribed to the topic.

**Cause:**

The Gazebo differential-drive plugin was configured to publish wheel TFs directly, but the wheel joint states were not being published for `robot_state_publisher`.

**Fix:**

- Added the Gazebo joint-state publisher plugin.
- Configured it to publish the left and right wheel joint states at 50 Hz.
- Disabled direct wheel TF publishing in the differential-drive plugin using `publish_wheel_tf=false`.

**Expected Result:**

Gazebo publishes wheel joint states, and `robot_state_publisher` uses those states to publish the corresponding wheel transforms.

**Verification:** Final joint-state and TF output should be checked after a clean launch.

---

### Bug 2: Incorrect `ament_package()` Declaration

**Area:** `testbed_description/CMakeLists.txt`

**Problem:**

The package build encountered an issue in the CMake configuration because `ament_package` was written without parentheses.

**Cause:**

The CMake command was written as:

`ament_package`

instead of:

`ament_package()`

**Fix:**

Corrected the declaration to `ament_package()`.

**Result:**

The `testbed_description` package built successfully after the correction.

---

### Bug 3: RViz Fixed Frame and TF Availability

**Area:** RViz2 / TF Configuration

**Problem:**

During RViz testing, the expected `map` fixed frame was not available at one stage. Changing the fixed frame to `base_link` or checking the relationship between `odom` and `base_link` showed that the TF tree was not yet available as expected.

**Investigation:**

The TF relationships between `map`, `odom`, and `base_link` were checked along with the localization and navigation launch processes.

**Fix / Resolution:**

The TF and localization setup was investigated and adjusted during the bringup debugging process.

**Verification:** The final `map → odom → base_link` transform chain should be confirmed during a fresh complete launch.

---
### Bug 3: Incorrect Map Image Path

**Area:** Map Server / Map Configuration

**Problem:**

During localization bringup, the map server could not load the map correctly because the image path specified in the map YAML configuration did not point to the correct map image location.

**Cause:**

The image path in the map YAML file was incorrect for the project directory structure.

**Fix:**

Updated the image path in the map YAML configuration to point to the correct map image file.

**Expected Result:**

The map server should load the occupancy map successfully, allowing AMCL and Nav2 to use the map for localization and navigation.

**Verification:** Confirmed by checking that the map is available in the running navigation setup.

---

### Bug 4: RViz Fixed Frame and TF Availability

**Area:** RViz2 / TF Configuration

**Problem:**

During RViz testing, the expected `map` fixed frame was not available at one stage. Changing the fixed frame to `base_link` or checking the relationship between `odom` and `base_link` showed that the TF tree was not yet available as expected.

**Investigation:**

The TF relationships between `map`, `odom`, and `base_link` were checked along with the localization and navigation launch processes.

**Fix / Resolution:**

The TF and localization setup was investigated and adjusted during the bringup debugging process.

**Verification:** The final `map → odom → base_link` transform chain should be confirmed during a fresh complete launch.

## 3. Final Testing

The simulation and navigation bringup were tested during development.

The following areas were checked:

- Gazebo robot spawning and simulation.
- Robot movement using differential-drive control.
- Joint state and TF publishing.
- Map server and AMCL localization.
- Nav2 bringup and costmap topics.
- RViz robot and map visualization.

Some checks should be repeated from a clean workspace build before final submission.

## 4. Notes

This report documents the issues encountered during development and the corresponding corrections. It is based on actual debugging observations rather than listing every configuration change as a bug.

Further issues identified during the final comparison and testing of the development branch will be added if required.

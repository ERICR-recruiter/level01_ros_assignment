# Bugs Identified and Debugging Observations

This document records issues identified while investigating the ERIC Robotics Testbed T1.0.0 starter packages.

## 1. Missing Parentheses in CMakeLists.txt

**Package:** `testbed_description`

**File:** `CMakeLists.txt`

**Issue:**

The `ament_package` statement was missing its parentheses.

Incorrect:
```cmake
ament_package
```

Correction:
```cmake
ament_package()
```

**Result:** Corrected the CMake statement.

## 2. Incorrect XML Tag Syntax in Gazebo Configuration

**File:** `testbed_description/urdf/testbed.gazebo`

**Location:** Around line 40, inside the `imu_link_1` configuration.

**Issue:**

An extra `>` character was present in the XML tag associated with `initial_orientation_as_reference`.

**Correction:**

Corrected the XML tag syntax by removing the extra character.

**Result:** Source-code syntax issue corrected.

## 3. RViz TF Message Filter Warning

**Observation:**

RViz displayed the following warning:

```text
Message Filter dropping message:
frame 'lidar_link_1'

Reason:
The timestamp on the message is earlier than
all the data in the transform cache.
```

**Investigation:**

The warning was observed while inspecting the robot's TF and sensor data.

**Status:** Root cause not yet confirmed.

Further investigation is required to determine whether the issue is related to simulation timestamps, TF availability or sensor message timing.

## 4. Additional Debugging Notes

The following activities were performed during the initial investigation:

- Inspected robot joint-state messages using `/joint_states`.
- Examined the robot TF tree.
- Generated TF tree visualizations using `view_frames`.
- Inspected the robot description and simulation launch files.

Additional issues and their resolutions will be documented as development progresses.
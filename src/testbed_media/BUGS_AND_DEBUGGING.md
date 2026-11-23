# Bugs and Debugging Record
## ERIC Robotics Testbed T1.0.0

This document records the errors encountered, debugging observations, root causes, and corrective actions performed while configuring and testing the ERIC Robotics Testbed T1.0.0 using ROS 2 Jazzy and Gazebo.

The objective is to document the actual debugging process, including build-time errors, launch-time errors, visualization problems, TF issues, lifecycle management, and robot navigation behaviour.

---

# 1. Missing Parentheses in CMakeLists.txt

**Package:** `testbed_description`  
**File:** `CMakeLists.txt`

### Issue

The `ament_package` statement was missing its parentheses.

**Incorrect:**

```cmake
ament_package
```

**Correction:**

```cmake
ament_package()
```

### Root Cause

Incorrect CMake function syntax.

### Resolution

Added the missing parentheses.

**Status:** FIXED

---

# 2. Incorrect XML Tag Syntax in Gazebo Configuration

**File:** `testbed_description/urdf/testbed.gazebo`

**Location:** Around line 40, inside the `imu_link_1` configuration.

### Issue

An extra `>` character was present in the XML tag associated with `initial_orientation_as_reference`.

### Resolution

Removed the extra character and corrected the XML syntax.

**Status:** FIXED

---

# 3. RViz TF Message Filter Timestamp Warning

**Component:** LiDAR / TF / RViz

### Observed Error

```text
[rviz2] Message Filter dropping message:

frame 'lidar_link_1'

Reason:
The timestamp on the message is earlier than
all the data in the transform cache.
```

### Investigation

The warning appeared while displaying LiDAR data in RViz.

The following components were investigated:

- LiDAR frame: `lidar_link_1`
- TF availability and transform timestamps.
- Robot description.
- Simulation clock.
- TF tree using `view_frames`.
- Joint-state messages.
- Simulation launch configuration.

### Investigation Notes

The warning indicated that RViz could not find a suitable transform for the incoming sensor message at its timestamp.

Possible areas investigated:

1. Simulation clock synchronization.
2. TF availability at the sensor message timestamp.
3. Sensor message timing.
4. Transform publication.

**Status:** ROOT CAUSE NOT CONFIRMED

Further investigation is required.

---

# 4. TF_OLD_DATA Warning on Robot Wheel Frames

**Component:** Robot State Publisher / TF / RViz

### Observed Error

```text
Warning: TF_OLD_DATA ignoring data from the past
for frame left_wheel_1

Warning: TF_OLD_DATA ignoring data from the past
for frame right_wheel_1
```

### Investigation

The warning appeared repeatedly for the robot's wheel frames.

The following checks were performed:

- Inspected `/tf`.
- Inspected `/tf_static`.
- Checked `/joint_states`.
- Inspected active ROS nodes.
- Checked simulation clock.
- Examined robot-state-publisher launch configurations.

### Root Cause Identified

Two separate launch files were starting `robot_state_publisher`.

**First instance:**

`robot_description.launch.py`

**Second instance:**

`testbed_rviz_barebones.launch.py`

Both instances were publishing robot transforms.

This resulted in duplicate transform publishers for the robot links and wheel frames.

### Additional Investigation

The simulation clock was inspected:

```bash
ros2 topic echo /clock
```

Simulation time was observed increasing.

The `use_sim_time` parameter was also configured for relevant nodes.

### Resolution

Removed the duplicate `robot_state_publisher` and standalone `joint_state_publisher` responsibilities from:

`testbed_rviz_barebones.launch.py`

The robot description and TF publication responsibilities were retained in:

`robot_description.launch.py`

Also configured:

```python
{'use_sim_time': True}
```

### Result

After removing the duplicate publisher and restarting the launch files, the `TF_OLD_DATA` warning disappeared.

**Status:** FIXED

---

# 5. robot_description Parameter YAML Parsing Error

**Package:** `testbed_bringup`

**Affected Launch Files:**

- `robot_description.launch.py`
- `testbed_rviz_barebones.launch.py`
- `testbed_full_bringup.launch.py`

### Observed Error

```text
[ERROR] [launch]: Caught exception in launch:

Unable to parse the value of parameter
robot_description as yaml.

If the parameter is meant to be a string,
try wrapping it in:

launch_ros.parameter_descriptions.ParameterValue(
    value,
    value_type=str
)
```

### Root Cause

The generated URDF content from the Xacro file was not explicitly declared as a string parameter.

ROS 2 launch parameter handling attempted to interpret the robot description as YAML.

### Resolution

Imported `ParameterValue`:

```python
from launch_ros.parameter_descriptions import ParameterValue
```

Wrapped the Xacro command:

```python
robot_description_content = ParameterValue(
    Command([
        FindExecutable(name="xacro"),
        " ",
        PathJoinSubstitution([
            FindPackageShare("testbed_description"),
            "urdf",
            "testbed.xacro",
        ]),
    ]),
    value_type=str
)
```

Passed the generated description to the node:

```python
robot_description = {
    "robot_description": robot_description_content
}
```

Applied the same parameter-handling approach to the RViz barebones launch configuration.

**Status:** CORRECTIVE CHANGE IMPLEMENTED

---

# 6. RViz Map Display - No Map Received

**Component:** Map Server / RViz / QoS

### Observed Issue

The launch file executed successfully, and RViz opened.

However, the Map display showed:

```text
Status: No map received
```

### Investigation

The map was not being received by the RViz Map display despite the launch process running.

The investigation focused on the Quality of Service (QoS) configuration of the map topic.

### Root Cause

A QoS durability mismatch was identified.

The map publisher and RViz subscriber were not configured with compatible durability settings.

The map publisher used transient-local durability, while the RViz Map display was configured with volatile durability.

### Resolution

Changed the RViz Map display QoS durability setting:

**Before:**

```text
Durability: Volatile
```

**After:**

```text
Durability: Transient Local
```

### Technical Understanding

Transient-local durability allows a publisher to retain previously published data for compatible late-joining subscribers.

This is important for map publication because the map may be published before RViz subscribes to the topic.

### Result

Updated the Map display QoS configuration to use transient-local durability.

**Status:** CORRECTIVE CHANGE APPLIED

---

# 7. Circular Package Dependencies During Colcon Build

**Component:** ROS 2 Workspace / Package Dependencies

### Observed Error

```text
ERROR:colcon:colcon build:

Unable to order packages topologically:

testbed_bringup: ['testbed_navigation']

testbed_localization:
['testbed_bringup', 'testbed_navigation']

testbed_navigation:
['testbed_bringup']
```

### Investigation

The error occurred while building the ROS 2 workspace:

```bash
cd ~/ros_nav2_assignment_ws

colcon build
```

Colcon attempted to determine the correct build order based on package dependencies.

However, it could not establish a valid topological ordering.

### Root Cause

A circular dependency existed between:

- `testbed_bringup`
- `testbed_navigation`

The dependency chain was:

```text
testbed_bringup
       |
       v
testbed_navigation
       |
       v
testbed_bringup
```

`testbed_localization` also depended on both packages.

This created a dependency cycle.

### Dependency Investigation

The intended dependency arrangement was:

```text
testbed_bringup
       |
       |----> testbed_navigation
       |
       |----> testbed_localization
```

The dependency declarations needed to be reviewed in the respective `package.xml` files.

### Required Correction

Keep the runtime dependencies in:

`testbed_bringup/package.xml`

```xml
<exec_depend>testbed_navigation</exec_depend>
<exec_depend>testbed_localization</exec_depend>
```

Review the reverse dependency from `testbed_navigation` to `testbed_bringup`.

The reciprocal dependency must be removed or the package responsibilities reorganized to eliminate the cycle.

### Technical Understanding

Colcon uses package dependency information to determine the build order.

Circular dependencies prevent it from establishing a valid topological ordering.

**Status:** DEPENDENCY ISSUE IDENTIFIED — VERIFY AFTER CORRECTION

---

# 8. Map Server Lifecycle Transition Failure

**Component:** Nav2 Map Server / Lifecycle Manager

### Observed Error

```text
[lifecycle_manager_map]:
Failed to change state for node: map_server
```

### Investigation

The error occurred during map-server lifecycle management.

The lifecycle manager attempted to change the state of `map_server`, but the transition failed.

### Possible Cause Investigated

Leftover `map_server` or lifecycle-related processes from previous launch sessions.

Old processes could interfere with subsequent launch attempts.

### Resolution Attempt

Terminate lingering map-server processes before relaunching:

```bash
pkill -f map_server
```

ROS 2 daemon restart was also used as an additional cleanup action:

```bash
ros2 daemon stop

ros2 daemon start
```

### Result

Process cleanup was used as a troubleshooting measure before relaunching the system.

**Status:** CLEANUP WORKAROUND APPLIED — VERIFY LIFECYCLE TRANSITION

---

# 9. Robot Navigation - Continuous Rotation and Goal-Reaching Failure

**Component:** Nav2 / Controller Server / Planner Server

### Observed Behaviour

During navigation testing, the robot exhibited unexpected rotational behaviour.

The following issues were observed:

1. Initial robot movement took time.
2. The robot rotated before making forward progress.
3. The robot continuously rotated near the goal.
4. The robot failed to reach the target position.
5. The robot sometimes rotated in an unexpected direction.
6. The robot performed excessive rotation instead of completing the navigation task.

### Investigation

The navigation configuration was investigated, particularly:

- Controller Server parameters.
- Planner Server parameters.
- Local costmap configuration.
- Global costmap configuration.
- Goal-reaching behaviour.
- Controller velocity and rotation behaviour.

### Debugging Approach

Controller Server and Planner Server parameters were adjusted iteratively through testing.

The configuration changes were based on observed robot behaviour.

This involved a trial-and-error approach to understand how parameter changes affected:

- Robot rotation.
- Path following.
- Angular velocity.
- Goal approach.
- Final goal-reaching behaviour.

### Specific Observations

**Observation 1: Initial Rotation**

The robot took time to begin moving and performed rotation before progressing towards the goal.

**Observation 2: Continuous Rotation Near Goal**

The robot approached the goal but continued rotating instead of completing the navigation task.

**Observation 3: Unexpected Rotation Direction**

The robot exhibited excessive rotation towards the right, even when a shorter rotation in the opposite direction appeared possible.

**Observation 4: Goal-Reaching Failure**

The robot continued rotating near the target position and failed to satisfy the goal-reaching condition.

### Investigation Status

Controller Server and Planner Server parameters were adjusted iteratively.

However, the navigation behaviour required further tuning and verification.

The final controller and planner configuration should be documented separately after successful testing.

**Status:** UNDER INVESTIGATION

---

# 10. Summary of Debugging Status

| No. | Issue | Status |
|---|---|---|
| 1 | Missing parentheses in `ament_package()` | Fixed |
| 2 | Incorrect XML tag syntax | Fixed |
| 3 | RViz LiDAR TF timestamp warning | Root cause not confirmed |
| 4 | TF_OLD_DATA on wheel frames | Fixed |
| 5 | `robot_description` YAML parsing error | Corrective change implemented |
| 6 | RViz Map QoS durability mismatch | Corrective change applied |
| 7 | Circular package dependencies | Identified; verify correction |
| 8 | Map server lifecycle transition failure | Cleanup workaround applied |
| 9 | Robot continuous rotation and goal failure | Under investigation |

---

# 11. Debugging Experience and Technical Learnings

During the investigation, the following technical areas were explored:

1. ROS 2 package configuration and CMake.
2. XML and URDF/Xacro syntax.
3. ROS 2 launch files and parameter handling.
4. Robot description publication.
5. TF tree and transform timestamps.
6. Simulation clock synchronization.
7. QoS durability and map publication.
8. ROS 2 package dependency management.
9. Lifecycle nodes and process management.
10. Nav2 controller and planner parameter tuning.

### Key Learnings

- A successful workspace build does not guarantee successful runtime execution.
- Launching RViz does not guarantee that sensor data or maps will be received.
- QoS compatibility is important for communication between ROS 2 publishers and subscribers.
- Multiple publishers for the same robot transforms can cause TF problems.
- Simulation time must be consistent across relevant simulation nodes.
- Circular package dependencies prevent successful topological ordering.
- Lifecycle nodes require correct state transitions.
- Navigation behaviour must be evaluated through actual robot movement, not just successful node startup.
- Controller and planner parameters should be tuned systematically based on observed robot behaviour.

---

**Documentation Note:** This record distinguishes confirmed fixes, corrective changes, workarounds, and unresolved issues. Issues should only be marked fully resolved after successful verification.
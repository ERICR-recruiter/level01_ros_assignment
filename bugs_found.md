# Bugs Found & Fixes — Testbed-T1.0.0 Starter Code

## 1. Map YAML points to a nonexistent image file
**File:** `testbed_bringup/maps/testbed_world.yaml`
`image: wrong_path_testbed_world.pgm` — the actual file is `testbed_world.pgm`.
`map_server` fails to load the map with the wrong path.
**Fix:** changed to `image: testbed_world.pgm`.

## 2. `ament_package` missing its call parentheses
**File:** `testbed_description/CMakeLists.txt`
`ament_package` with no `()` is invalid CMake syntax — `colcon build` fails to
even configure `testbed_description`.
**Fix:** changed to `ament_package()`.

## 3. Malformed XML in the IMU plugin block (stray `>`)
**File:** `testbed_description/urdf/testbed.gazebo`
`</initial_orientation_as_reference>>` has an extra trailing `>`, breaking XML
parsing of the xacro file — `robot_description` never gets generated.
**Fix:** removed the stray `>`.

## 4. Lidar max range far too short for the map (1.5 m in a ~20 m room)
**File:** `testbed_description/urdf/testbed.gazebo` (lidar sensor block)
The map (405×400 px @ 0.05 m/px) and world file (walls ~±10 m from center)
describe a ~20 m × 20 m room, but the lidar's `<max>` range was only 1.5 m —
it can't see any wall from mid-room, starving AMCL/costmaps of data.
**Fix:** increased `<max>` to `10.0` m.

## 5. `robot_state_publisher` not synced to simulation time
**File:** `testbed_description/launch/robot_description.launch.py`
No `use_sim_time` param, while the provided barebones launch file does set it —
causes TF timestamps to drift off Gazebo's sim clock (TF extrapolation warnings).
**Fix:** added `{'use_sim_time': True}` to the node's parameters.
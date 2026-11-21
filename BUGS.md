# BUGS.md: Starter Code Bugs (Level 01 ROS Assignment)

Environment: Ubuntu, ROS 2 Humble, Gazebo Classic 11, workspace `~/assignment_ws`, branch `fix/starter-bugs`.
Original (unmodified) commit: `6086b81`.

Every bug below was found in the starter packages `testbed_description`, `testbed_gazebo` and `testbed_bringup`. Each entry gives the file, the symptom, the cause, the fix and the check that confirmed it. Where a bug was found by reading the code rather than by watching it fail, the entry says so.

## Summary

| # | Bug | File | How found | Commit |
|---|-----|------|-----------|--------|
| 1 | `ament_package` missing `()` | `testbed_description/CMakeLists.txt` | Build failure | `d7e788f` |
| 2 | Map yaml points to a non-existent image | `testbed_bringup/maps/testbed_world.yaml` | map_server failure | `c0845b4` |
| 3 | `maps/` directory never installed | `testbed_bringup/CMakeLists.txt` | Inspected `install/` | see `git log` |
| 4 | Lidar max range only 1.5 m | `testbed_description/urdf/testbed.gazebo` | Code inspection | `5cc72ba` |
| 5 | Stray `>` in IMU plugin XML | `testbed_description/urdf/testbed.gazebo` | Code inspection | `098f7c1` |
| 6 | `robot_state_publisher` has no `use_sim_time` | `testbed_description/launch/robot_description.launch.py` | Code inspection | `90ef920` |
| 7 | CRLF line endings in a launch script | `testbed_description/launch/robot_description.launch.py` | `file` command | `61b0036` |
| 8 | Missing `exec_depend` entries | three `package.xml` files | Code inspection | `18057d1` |

---

## Bug 1: `ament_package` missing parentheses

- **File:** `testbed_description/CMakeLists.txt`, last line
- **Symptom:** the package does not build.
- **Cause:** the file ended with `ament_package` instead of `ament_package()`. CMake cannot parse a command name without its argument list.
- **Fix:** `ament_package` → `ament_package()`

**Before** (`colcon build --packages-select testbed_description` on the original file):

```
Starting >>> testbed_description
--- stderr: testbed_description
CMake Error at CMakeLists.txt:24:
  Parse error.  Expected "(", got newline with text "

  ".

Failed   <<< testbed_description [0.06s, exited with code 1]

Summary: 0 packages finished [0.61s]
  1 package failed: testbed_description
```

**After:**

```
Summary: 1 package finished [0.94s]
```

## Bug 2: Map yaml points to a non-existent image

- **File:** `testbed_bringup/maps/testbed_world.yaml`, line 1
- **Symptom:** the map server cannot configure.
- **Cause:** `image: wrong_path_testbed_world.pgm`. The real file is `testbed_world.pgm`.
- **Fix:** `image: testbed_world.pgm`

**Before** (map_server launched with the original yaml, then configured):

```
$ ros2 lifecycle set /map_server configure
Transitioning failed
```

**After:**

```
$ ros2 lifecycle set /map_server configure
Transitioning successful
$ ros2 lifecycle set /map_server activate
Transitioning successful
$ ros2 topic echo /map --once --no-arr
...
info:
  resolution: 0.05000000074505806
  width: 405
  height: 400
  origin:
    position: {x: -10.2, y: -9.94, z: 0.0}
```

## Bug 3: `maps/` directory never installed

- **File:** `testbed_bringup/CMakeLists.txt`
- **Symptom:** after `colcon build`, the map files are missing from the install space, so any launch file that looks for them in `share/testbed_bringup/maps` fails.
- **Cause:** the `install(DIRECTORY ...)` block listed only `launch`.
- **Fix:**

```cmake
install(
  DIRECTORY
    launch
    maps
  DESTINATION
    share/${PROJECT_NAME}/
)
```

**Before** (`ls install/testbed_bringup/share/testbed_bringup/`):

```
cmake        launch            local_setup.sh   package.dsv  package.xml
environment  local_setup.bash  local_setup.zsh  package.ps1  package.zsh
hook         local_setup.dsv   package.bash     package.sh
```

**After** (`ls install/testbed_bringup/share/testbed_bringup/maps`):

```
testbed_world.pgm  testbed_world.yaml
```

The map server was later started from this installed path with no errors, which confirms Bugs 2 and 3 together.

## Bug 4: Lidar max range only 1.5 m

- **File:** `testbed_description/urdf/testbed.gazebo`, lidar `<range>` block
- **Symptom:** the lidar sees only 1.5 m around the robot, which is far too short for a 20 m × 20 m map. AMCL and the costmaps would barely work.
- **Cause:** `<max>1.5</max>`. Found by reading the sensor definition.
- **Fix:** `<max>12.0</max>`

**After** (full bringup running):

```
$ ros2 topic echo /scan --once | grep range_max
range_max: 12.0
$ ros2 topic hz /scan
average rate: 29.380
```

In RViz the `/scan` points reach the room walls.

## Bug 5: Stray `>` in the IMU plugin

- **File:** `testbed_description/urdf/testbed.gazebo`, IMU plugin block
- **Symptom:** none visible. It is a typo in the XML.
- **Cause:** `<initial_orientation_as_reference>false</initial_orientation_as_reference>>` had an extra `>`. Found by reading the file.
- **Fix:** removed the extra `>`.
- **After:** the full bringup starts and `/imu` is listed by `ros2 topic list`.

## Bug 6: `robot_state_publisher` has no `use_sim_time`

- **File:** `testbed_description/launch/robot_description.launch.py`
- **Symptom (expected from the code):** TF stamps use the wall clock while Gazebo uses `/clock`. Nav2 later rejects those transforms. Found by reading the launch file, not by watching a failure.
- **Cause:** the node's parameters contained only the robot description.
- **Fix:**

```python
parameters=[robot_description, {'use_sim_time': True}]
```

**After:**

```
$ ros2 param get /robot_state_publisher use_sim_time
Boolean value is: True
```

`view_frames` timestamps are in simulation time (around 215 s at that point in the run).

## Bug 7: CRLF line endings in a launch script

- **File:** `testbed_description/launch/robot_description.launch.py`
- **Symptom:** Windows line endings in a script with a `#!/usr/bin/env python3` shebang. Running it directly can fail with a bad-interpreter error.
- **Check on the original:** `git show 6086b81:testbed_description/launch/robot_description.launch.py | file -` reports `with CRLF line terminators`.
- **Fix:** converted to LF (`dos2unix`).
- **After:** `file testbed_description/launch/robot_description.launch.py` reports `ASCII text executable` with no CRLF note.

## Bug 8: Missing `exec_depend` entries

- **Files:** `testbed_description/package.xml`, `testbed_gazebo/package.xml`, `testbed_bringup/package.xml`
- **Symptom:** the launch files use `xacro`, `robot_state_publisher`, `joint_state_publisher`, `rviz2`, `gazebo_ros` and the sibling packages, but none were declared. A user running `rosdep install` on a clean machine would not get them.
- **Fix:**
  - `testbed_description`: `xacro`, `robot_state_publisher`, `joint_state_publisher`, `rviz2`
  - `testbed_gazebo`: `gazebo_ros`
  - `testbed_bringup`: `rviz2`, `testbed_gazebo`, `testbed_description`
  - The `TODO` description and license fields were also filled in.

**After:**

```
$ rosdep check --from-paths src --ignore-src
All system dependencies have been satisfied
$ colcon build --symlink-install
Summary: 3 packages finished [1.81s]
```

---

## Checked and not a bug

These items looked suspicious when reading the code. Each was tested and behaved correctly, so nothing was changed because of them.

### `world` launch argument in `spawn_playground.launch.py`

The argument is declared but not passed to the Gazebo include, which looked like it would open an empty world. In practice `ros2 launch testbed_gazebo spawn_playground.launch.py` on the original file loaded the playground world with no errors, because an included launch file inherits the parent's launch configurations. An explicit `launch_arguments={'world': LaunchConfiguration('world')}.items()` is harmless and makes the intent clearer, but it is not a fix.

### `libgazebo_ros_control.so` plugin in `testbed.gazebo`

Nothing in the repo uses `ros2_control`, so this plugin looked like it might fail to load. Searching the full-bringup launch log (`grep -r -n "libgazebo_ros_control" ~/.ros/log/<run>/`) returned no matches, and the same log contained the `spawn_entity` lines, so the right run was searched. No error appeared and the plugin was left alone.

### Wheel friction (`mu1`/`mu2` = 0.2)

Low friction can make wheels slip. A drive test at 0.2 m/s for 4 s moved the robot from `/odom` x ≈ -0.03 to x ≈ 0.81, about 0.84 m, which is what the command asks for. With the robot stopped, the drift over 10 s fell from about 3.6 mm to about 0.5 mm on repeated checks, which is the robot settling after a drive. The values were left unchanged.

Note: the diff-drive odometry starts at the spawn pose (about y = 5), which indicates world-based odometry, so comparing `/odom` against Gazebo's pose cannot reveal slip. The test above relies on commanded versus reported travel and on the idle-drift check.

### World pose versus the map (`test_room` pose in `testbed_playground.world`)

The `<model>` pose and `<state>` pose of `test_room` differ, which looked like it could shift the walls away from the map. With the map server running, a temporary identity `map → odom` transform and RViz Fixed Frame set to `map`, the live `/scan` points sit on the wall lines of the map. The world and the map agree, so no change was needed.
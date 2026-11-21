# 🐛 BUGS.md: Starter Code Bugs

The starter code had a few bugs hiding in it on purpose. Here's what I found, how I spotted each one, and how I squashed it.

**Setup:** Ubuntu 22.04, ROS 2 Humble, Gazebo Classic 11, workspace `~/assignment_ws`
**Original commit:** `6086b81`. Every bug got its own fix commit.

## Quick list

| # | What was wrong | Where | How I found it | Commit |
|---|---|---|---|---|
| 1 | `ament_package` missing its `()` | `testbed_description/CMakeLists.txt` | Build blew up | `d7e788f` |
| 2 | Map yaml pointed to the wrong image name | `testbed_bringup/maps/testbed_world.yaml` | map_server wouldn't configure | `c0845b4` |
| 3 | `maps/` folder never got installed | `testbed_bringup/CMakeLists.txt` | Peeked in the `install/` folder | `fa6f051` |
| 4 | Lidar only saw 1.5 m | `testbed_description/urdf/testbed.gazebo` | Read the sensor config | `5cc72ba` |
| 5 | Random extra `>` in the IMU plugin | `testbed_description/urdf/testbed.gazebo` | Read the file | `098f7c1` |
| 6 | `robot_state_publisher` had no `use_sim_time` | `testbed_description/launch/robot_description.launch.py` | Read the launch file | `90ef920` |
| 7 | Windows line endings in a launch script | `testbed_description/launch/robot_description.launch.py` | `file` command | `61b0036` |
| 8 | Missing `exec_depend` entries | three `package.xml` files | Read the launch files | `18057d1` |

## The bugs

### 1. `ament_package` missing `()`
- **Found it:** `colcon build` crashed with a CMake parse error ("Expected `(`").
- **Fix:** `ament_package` → `ament_package()`. Tiny change, big difference.
- **Proof:** package builds now.

### 2. Map yaml pointed to the wrong image
- **Found it:** `map_server` refused to configure (`Transitioning failed`).
- **What was up:** the yaml said `wrong_path_testbed_world.pgm`, but the real file is `testbed_world.pgm`.
- **Fix:** `image: testbed_world.pgm`.
- **Proof:** map_server configured and activated, and `/map` showed up (405 × 400 cells, 0.05 m).

### 3. `maps/` folder never installed
- **Found it:** after building, `maps/` wasn't in `install/testbed_bringup/share/testbed_bringup/`, so any launch file looking for the map would fail.
- **What was up:** the `install(DIRECTORY ...)` block only had `launch` in it.
- **Fix:** added `maps` next to `launch`.
- **Proof:** `testbed_world.pgm` and `testbed_world.yaml` now sit in the install folder.

### 4. Lidar only saw 1.5 m
- **Found it:** read the lidar `<range>` block. 1.5 m is way too short for a 20 m × 20 m map, so AMCL and the costmaps would've been basically blind.
- **Fix:** `<max>1.5</max>` → `<max>12.0</max>`.
- **Proof:** `/scan` shows `range_max: 12.0` at about 29 Hz, and the scan points reach the walls in RViz.

### 5. Extra `>` in the IMU plugin
- **Found it:** spotted `</initial_orientation_as_reference>>` while reading the XML. Nothing visibly broke, it's just a typo.
- **Fix:** deleted the extra `>`.
- **Proof:** full bringup starts fine and `/imu` shows up in the topic list.

### 6. `robot_state_publisher` had no `use_sim_time`
- **Found it:** read the launch file and saw it only passed the robot description. That means TF would use wall-clock time while Gazebo runs on sim time, and Nav2 rejects mismatched transforms.
- **Fix:** `parameters=[robot_description, {'use_sim_time': True}]`.
- **Proof:** `ros2 param get /robot_state_publisher use_sim_time` says `True`.

### 7. Windows line endings in a launch script
- **Found it:** `git show 6086b81:<file> | file -` said "CRLF line terminators". A script with a shebang and Windows line endings can fail to run.
- **Fix:** converted to LF with `dos2unix`.
- **Proof:** `file` now says plain `ASCII text`.

### 8. Missing `exec_depend` entries
- **Found it:** the launch files use `xacro`, `robot_state_publisher`, `joint_state_publisher`, `rviz2`, `gazebo_ros` and the sibling packages, but none were declared. Someone running `rosdep install` on a fresh machine would've missed all of them.
- **Fix:** added the missing `exec_depend` tags to the three `package.xml` files.
- **Proof:** `rosdep check` says all dependencies are satisfied, and `colcon build` finishes for all 3 packages.

## Looked sketchy, but turned out fine

I tested these and they all worked, so I left them alone.

| Thing | Why it looked suspicious | What actually happened |
|---|---|---|
| `world` argument in `spawn_playground.launch.py` | Declared but never passed to the Gazebo include | Playground world still loaded, since included launch files inherit the parent's launch configs |
| `libgazebo_ros_control.so` plugin | Nothing here uses `ros2_control` | No errors in the bringup log, so I left it |
| Wheel friction (`mu1`/`mu2` = 0.2) | Low friction can mean slipping | Drove at 0.2 m/s for 4 s and moved about 0.84 m, as commanded. Idle drift was only a few mm |
| `test_room` pose in the world file | Model pose and state pose differ, so walls might be off the map | Live `/scan` points lined up with the map walls |
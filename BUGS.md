# Bug Report: Testbed-T1.0.0 Starter Code

**Environment:** Ubuntu 22.04 · ROS 2 Humble · Gazebo 11.10.2

## Summary

| # | File | Bug | Fix | Severity |
|---|------|-----|-----|----------|
| 1 | `testbed_description/CMakeLists.txt` | `ament_package` missing `()` | Added `()` | Build |
| 2 | `testbed_description/urdf/testbed.gazebo` | Lidar `range_max` only 1.5 m, so the scan is all `inf` | Set to 12.0 m | Functional |
| 3 | `testbed_bringup/CMakeLists.txt` | `maps/` not installed | Added `maps` to `install(DIRECTORY)` | Runtime |
| 4 | `testbed_gazebo/CMakeLists.txt` | `models/` not installed, but added to `GAZEBO_MODEL_PATH` | Added `models` to `install(DIRECTORY)` | Minor |
| 5 | `testbed_description/urdf/testbed.gazebo` | Loads ROS 1 plugin `libgazebo_ros_control.so` | Removed the plugin block | Minor |
| 6 | `testbed_description/launch/robot_description.launch.py` | `robot_state_publisher` runs on wall time | Added `use_sim_time: True` | Functional |

**Severity:** Build = `colcon build` fails · Runtime = node/launch crashes · Functional = runs but misbehaves · Minor = cleanup

---

## Details

### 1. `ament_package` missing `()`
- **Symptom:** `colcon build` fails: `CMake Error at CMakeLists.txt:24: Parse error. Expected "("`
- **Found by:** Line 24 is the end of the file, so the error is on line 23. Compared it with `testbed_bringup/CMakeLists.txt`, which builds.
- **Cause:** `ament_package()` is a CMake function call and needs `()`. Without it the package is never registered in the ament index.
- **Fix:** `ament_package` → `ament_package()`
- **Verified:** Clean `colcon build`; all 3 packages exit with code 0.

### 2. Lidar range too short (1.5 m)
- **Symptom:** `/scan` publishes at ~30 Hz but every range is `inf`, and no laser points appear in RViz. `range_max: 1.5`.
- **Found by:** `ros2 topic hz /scan` showed the sensor working, but `ros2 topic echo /scan --once` returned only `inf`. In Gazebo the walls are clearly several metres from the spawn point (about 3.4 m to the nearest one in the map).
- **Cause:** `<range><max>1.5</max>` in the lidar sensor is shorter than the distance to any wall, so the sensor never gets a hit. AMCL has nothing to match against the map, and the costmaps see no obstacles.
- **Fix:** `<max>1.5</max>` → `<max>12.0</max>`, a typical range for a low-cost 2D lidar (e.g. RPLidar A1) and enough to see walls across the ~20 m map.
- **Verified:** After relaunching, `/scan` contains finite ranges and laser points line up with the walls in RViz.

### 3. `maps/` not installed by `testbed_bringup`
- **Symptom:** `install/testbed_bringup/share/testbed_bringup/` contains only `launch/`, so `get_package_share_directory('testbed_bringup') + '/maps/testbed_world.yaml'` points to a missing file.
- **Found by:** Listed the installed share directory and compared it with the source package.
- **Cause:** `install(DIRECTORY ...)` in `CMakeLists.txt` listed only `launch`.
- **Fix:** Added `maps` to the `install(DIRECTORY ...)` list.
- **Verified:** After rebuilding, `maps/` is present in the installed share directory.

### 4. `models/` not installed by `testbed_gazebo`
- **Symptom:** `spawn_playground.launch.py` adds `share/testbed_gazebo/models` to `GAZEBO_MODEL_PATH`, but that directory doesn't exist after the build.
- **Found by:** Compared the path printed at launch (`GAZEBO MODELS PATH==...`) with the contents of the installed share directory.
- **Cause:** `install(DIRECTORY ...)` listed only `launch` and `worlds`.
- **Fix:** Added `models` to the `install(DIRECTORY ...)` list.
- **Verified:** After rebuilding, `models/` is installed. Note: this is a latent bug. The current world inlines all its models (0 `model://` references), so there was no visible failure yet.

### 5. ROS 1 `gazebo_ros_control` plugin in a ROS 2 robot
- **Symptom:** Gazebo log (`~/.gazebo/server-11345/default.log`): `[Err] [Plugin.hh:212] Failed to load plugin libgazebo_ros_control.so: cannot open shared object file`
- **Found by:** Searched the Gazebo server log for `[Err]`, then confirmed the library doesn't exist anywhere on the system.
- **Cause:** `libgazebo_ros_control.so` is the ROS 1 plugin. It doesn't exist in ROS 2 Humble, and nothing here needs it: `libgazebo_ros_diff_drive.so` already drives the wheels and publishes `/odom` and the `odom → base_footprint` TF. No ros2_control controllers are used.
- **Fix:** Removed the `<plugin name="control" filename="libgazebo_ros_control.so"/>` block.
- **Verified:** The error no longer appears in a fresh Gazebo log, and the robot still spawns and publishes `/odom`.

### 6. `robot_state_publisher` not using simulation time
- **Symptom:** `ros2 param get /robot_state_publisher use_sim_time` → `False`, while gazebo, diff_drive and RViz are `True`. `/tf_static` was stamped with wall-clock time (~1.79e9 s) while `/clock` was ~550 s.
- **Found by:** Checked `use_sim_time` on every node, then compared `/clock` with the `/tf_static` and `/odom` header stamps.
- **Cause:** `robot_description.launch.py` passes only `robot_description` to the node, so it defaults to wall time. The impact is small today because all of its joints are fixed (static TFs are timeless), but any moving joint would get stamps ~56 years ahead of sim time and cause TF extrapolation errors in Nav2 and AMCL.
- **Fix:** `parameters=[robot_description, {'use_sim_time': True}]`
- **Verified:** `use_sim_time` is now `True` and `/tf_static` is no longer stamped with wall-clock time.

---

## Investigated, not bugs
- **`[Err] [Sensor.cc:510] Get noise index not valid` (×6):** Gazebo prints this when a sensor (here the IMU) has no `<noise>` block. It's harmless and doesn't affect the sensor output.
- **`testbed.trans`:** ROS 1 transmission definitions that nothing reads in ROS 2. Left in place because they have no effect.

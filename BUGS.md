# Bug Report: Testbed-T1.0.0 Starter Code

**Environment:** Ubuntu 22.04 · ROS 2 Humble · Gazebo 11.10.2

## Summary

| # | File | Bug | Fix | Severity |
|---|------|-----|-----|----------|
| 1 | `testbed_description/CMakeLists.txt` | `ament_package` missing `()` | Added `()` | Build |
| 2 | `testbed_description/urdf/testbed.gazebo` | Lidar `range_max` only 1.5 m, so the scan is all `inf` | Set to 12.0 m | Functional |

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

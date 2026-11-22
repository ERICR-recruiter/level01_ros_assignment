# Bug Report: Testbed-T1.0.0 Starter Code

**Environment:** Ubuntu 22.04 · ROS 2 Humble · Gazebo 11.10.2

## Summary

| # | File | Bug | Fix | Severity |
|---|------|-----|-----|----------|
| 1 | `testbed_description/CMakeLists.txt` | `ament_package` missing `()` | Added `()` | Build |

**Severity:** Build = `colcon build` fails · Runtime = node/launch crashes · Functional = runs but misbehaves · Minor = cleanup

---

## Details

### 1. `ament_package` missing `()`
- **Symptom:** `colcon build` fails: `CMake Error at CMakeLists.txt:24: Parse error. Expected "("`
- **Found by:** Line 24 is the end of the file, so the error is on line 23. Compared it with `testbed_bringup/CMakeLists.txt`, which builds.
- **Cause:** `ament_package()` is a CMake function call and needs `()`. Without it the package is never registered in the ament index.
- **Fix:** `ament_package` → `ament_package()`
- **Verified:** Clean `colcon build`; all 3 packages exit with code 0.

# Bug Fixes
 
Eleven fixes across the `testbed_description`, `testbed_bringup` and `testbed_gazebo` packages, plus the RViz configuration.
 
## Summary
 
| # | Area | File | Fix |
|---|------|------|-----|
| 1 | Build | `testbed_description/CMakeLists.txt` | Added missing parentheses to `ament_package()` |
| 2 | Map | `testbed_bringup/maps/testbed_world.yaml` | Pointed `image` at the real map file |
| 3 | Install | `testbed_bringup/CMakeLists.txt` | Installed the `maps` directory |
| 4 | Install | `testbed_gazebo/CMakeLists.txt` | Installed the `models` directory |
| 5 | Simulation | `testbed_description/urdf/testbed.gazebo` | Removed a stray `>` in the IMU plugin |
| 6 | Simulation | `testbed_description/urdf/testbed.gazebo` | Raised LiDAR max range from 1.5 m to 10 m |
| 7 | Simulation | `testbed_description/urdf/testbed.gazebo` | Matched wheel separation to the URDF (0.346 m) |
| 8 | Simulation | `testbed_description/urdf/testbed.gazebo` | Set LiDAR field of view to 270° (Hokuyo-style) |
| 9 | Visualization | RViz configuration (`*.rviz`) | Set Map and costmap durability to Transient Local |
| 10 | Robot model | `testbed_description/urdf/testbed.xacro` | Moved `base_footprint` to the wheel midpoint |
| 11 | Robot model | `testbed_description/urdf/testbed.xacro` | Set caster friction to zero |
 
---
 
## Build and install
 
### 1. Missing parentheses on `ament_package`
 
- **File:** `testbed_description/CMakeLists.txt` (line 23)
- **Problem:** `ament_package` was written without parentheses, so CMake could not parse the file and the package failed to build.
- **Fix:** Changed it to `ament_package()`.
### 3. `maps` directory not installed
 
- **File:** `testbed_bringup/CMakeLists.txt` (lines 27-33)
- **Problem:** The `install(DIRECTORY ...)` rule copied only `launch`, so the map files never reached the install space and the map server could not find them.
- **Fix:** Added `maps` to the `install(DIRECTORY ...)` rule.
### 4. `models` directory not installed
 
- **File:** `testbed_gazebo/CMakeLists.txt` (lines 28-35)
- **Problem:** The `install(DIRECTORY ...)` rule copied only `launch` and `worlds`, leaving the Gazebo models out of the install space.
- **Fix:** Added `models` to the `install(DIRECTORY ...)` rule.
## Map
 
### 2. Wrong image path in the map YAML
 
- **File:** `testbed_bringup/maps/testbed_world.yaml` (line 1)
- **Problem:** The `image` field referred to `wrong_path_testbed_world.pgm`, which does not exist, so the map failed to load.
- **Fix:** Changed `image` to `testbed_world.pgm`.
## Simulation (Gazebo plugins)
 
All of these are in `testbed_description/urdf/testbed.gazebo`.
 
### 5. Stray closing bracket in the IMU plugin
 
- **Line:** 40
- **Problem:** The tag `<initial_orientation_as_reference>false</initial_orientation_as_reference>>` had a duplicate closing `>`. This made the XML invalid, so the IMU plugin could not load.
- **Fix:** Removed the extra `>`.
### 6. LiDAR range too short
 
- **Line:** 65
- **Problem:** The ray sensor's maximum range was `1.5` m, far too short for the indoor world, so most of the map was invisible to the scan.
- **Fix:** Changed `<max>1.5</max>` to `<max>10.0</max>`, which matches a real planar LiDAR and the size of the world.
### 7. Wheel separation does not match the URDF
 
- **Line:** 16
- **Problem:** The differential drive plugin used `<wheel_separation>0.35</wheel_separation>`. The wheel joints in `testbed.xacro` are at y = 0.135241 (left) and y = -0.210759 (right), a span of 0.346 m. The mismatch skews odometry.
- **Fix:** Changed the value to `<wheel_separation>0.346</wheel_separation>`.
### 8. LiDAR field of view set to 270°
 
- **Problem:** The simulated scan did not match the Hokuyo sensor it models, which covers 270°.
- **Fix:** Set the horizontal scan to -135° to +135° (±2.356194 rad) with 1081 samples (0.25° resolution), the Hokuyo UST/UTM layout. The 10 m maximum range from fix 6 matches the UST-10LX.
## Visualization
 
### 9. RViz subscribed to the map with the wrong durability
 
- **File:** RViz configuration (`*.rviz`)
- **Problem:** The Map and costmap displays used Volatile durability. `map_server` and Nav2 publish these topics once as Transient Local, so a Volatile subscriber that connects afterwards never receives the data and the display stays empty.
- **Fix:** Set Durability Policy to **Transient Local** and Reliability Policy to **Reliable** on the Map display (`/map`) and the global costmap display (`/global_costmap/costmap`).
## Robot model (URDF)
 
Both of these are in `testbed_description/urdf/testbed.xacro`.
 
### 10. `base_footprint` not at the wheel midpoint
 
- **Joint:** `fixed_base_joint` (`base_footprint` to `base_link`)
- **Problem:** `base_footprint` sat at the `base_link` origin, but the midpoint between the drive wheels is at about x = -0.0505, y = -0.0378 in the `base_link` frame. The differential drive plugin assumes the base frame is at the centre of the axle, so when the robot turned in place its frame swung around a small circle, which skewed odometry and AMCL.
- **Fix:** Changed the joint origin to `xyz="0.0505 0.0378 0"`, which places `base_footprint` on the ground at the wheel midpoint. Also removed the zero-size box visual from the `base_footprint` link, since it served no purpose.
### 11. Caster friction set to zero
 
- **Links:** `caster_1`, `caster_2`, `caster_3`, `caster_4`
- **Problem:** The casters are fixed joints with mesh collisions and used Gazebo's default friction (`mu` = 1). They dragged on the floor and resisted turning and sideways motion, so the robot stuttered or skidded.
- **Fix:** Added a `<gazebo reference="caster_N">` block for each caster with `<mu1>0.0</mu1>` and `<mu2>0.0</mu2>`, so the casters slide freely and only the drive wheels provide traction.
 
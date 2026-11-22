# Starter Code Bugs & Fixes Log

During the initial build, bringup, and simulation testing of the starter packages (`testbed_description`, `testbed_gazebo`, and `testbed_bringup`), several bugs were identified across CMake configurations, URDF modeling, simulation plugins, and coordinate frames.

All 9 issues and their fixes are documented below.

---

## Summary of Identified Bugs

| # | File / Component | Category | Summary of Issue |
|---|------------------|----------|------------------|
| 1 | `testbed_description/CMakeLists.txt` | Build / Syntax | Missing parentheses on `ament_package` |
| 2 | `testbed_bringup/maps/testbed_world.yaml` | Configuration | Incorrect image path for the map file |
| 3 | `testbed_bringup/CMakeLists.txt` | Build / Install | `maps/` directory not installed to share directory |
| 4 | `testbed_gazebo/CMakeLists.txt` | Build / Install | `models/` directory not installed to share directory |
| 5 | `testbed_description/urdf/testbed.gazebo` | Simulation | Obsolete ROS 1 Gazebo control plugin included |
| 6 | `testbed_description/urdf/testbed.gazebo` | Syntax | Stray bracket `>>` in IMU configuration |
| 7 | `testbed_description/urdf/testbed.gazebo` | Sensor Setup | LIDAR max range artificially capped at 1.5 m |
| 8 | `testbed_description/launch/robot_description.launch.py` | TF / Clock | Missing `use_sim_time: True` in `robot_state_publisher` |
| 9 | `testbed_description/urdf/testbed.gazebo` | Physics / Friction | Fixed caster friction causing severe odometry drift |

---

## Detailed Breakdown & Solutions

### 1. `testbed_description/CMakeLists.txt`: Build Syntax Error
- **Symptom:** Running `colcon build` failed immediately during CMake configuration for `testbed_description`.
- **Cause:** Line 23 was written as `ament_package` without closing parentheses.
- **Fix:** Changed line 23 to `ament_package()`.

```cmake
# Before
ament_package

# After
ament_package()
```

---

### 2. `testbed_bringup/maps/testbed_world.yaml`: Non-Existent Map Path
- **Symptom:** `nav2_map_server` crashed on bringup with an error stating the map file could not be found.
- **Cause:** The YAML configuration referenced `image: wrong_path_testbed_world.pgm`, while the actual file present in the directory is `testbed_world.pgm`.
- **Fix:** Corrected the image key in `testbed_world.yaml`.

```yaml
# Before
image: wrong_path_testbed_world.pgm

# After
image: testbed_world.pgm
```

---

### 3. `testbed_bringup/CMakeLists.txt`: Missing Maps Install Rule
- **Symptom:** Even after building the workspace, map files were absent from `install/testbed_bringup/share/testbed_bringup/`.
- **Cause:** `install(DIRECTORY ...)` only listed `launch` and omitted the `maps` folder.
- **Fix:** Added `maps` to the installation rule.

```cmake
install(
  DIRECTORY
    launch
    maps
  DESTINATION
    share/${PROJECT_NAME}/
)
```

---

### 4. `testbed_gazebo/CMakeLists.txt`: Missing Models Install Rule
- **Symptom:** Gazebo launched with warnings about missing model assets (`test_room`, `wooden_fence`), resulting in invisible or missing obstacles.
- **Cause:** The `models/` folder wasn't being installed into `share/testbed_gazebo/models/`.
- **Fix:** Added `models` to `install(DIRECTORY ...)` in `testbed_gazebo/CMakeLists.txt`.

```cmake
install(
  DIRECTORY
    launch
    worlds
    models
  DESTINATION
    share/${PROJECT_NAME}/
)
```

---

### 5. `testbed_description/urdf/testbed.gazebo`: Obsolete ROS 1 Plugin
- **Symptom:** Gazebo console printed dynamic library loading errors: `Failed to load plugin libgazebo_ros_control.so`.
- **Cause:** `libgazebo_ros_control.so` is a legacy ROS 1 plugin that does not exist in ROS 2 Humble. The robot's movement is already handled via `libgazebo_ros_diff_drive.so`.
- **Fix:** Removed the unused `<plugin name="control" filename="libgazebo_ros_control.so"/>` block.

---

### 6. `testbed_description/urdf/testbed.gazebo`: XML Syntax Typo
- **Symptom:** Minor XML parsing warning during xacro generation.
- **Cause:** Line 40 had an extra closing angle bracket: `</initial_orientation_as_reference>>`.
- **Fix:** Removed the extra `>` character.

```xml
<!-- Before -->
<initial_orientation_as_reference>false</initial_orientation_as_reference>>

<!-- After -->
<initial_orientation_as_reference>false</initial_orientation_as_reference>
```

---

### 7. `testbed_description/urdf/testbed.gazebo`: Severely Constrained LIDAR Range
- **Symptom:** When the robot was positioned near the center of a room, AMCL particles scattered widely and the robot was unable to localize against the map walls.
- **Cause:** The ray sensor's max range was set to `<max>1.5</max>`. In a room spanning over 10 meters, the laser beams couldn't reach any walls.
- **Fix:** Increased `<max>` range to `12.0` meters to provide adequate laser coverage across the environment.

```xml
<!-- Before -->
<range>
  <min>0.10</min>
  <max>1.5</max>
  <resolution>0.01</resolution>
</range>

<!-- After -->
<range>
  <min>0.10</min>
  <max>12.0</max>
  <resolution>0.01</resolution>
</range>
```

---

### 8. `testbed_description/launch/robot_description.launch.py`: TF Timestamp Desync
- **Symptom:** RViz constantly logged:  
  `Message Filter dropping message: ... timestamp on the message is earlier than all the data in the transform cache`.
- **Cause:** `robot_state_publisher` was started with system wall clock time instead of simulation time. Gazebo and the LIDAR sensor publish on `/clock`, causing a mismatch in the TF buffer.
- **Fix:** Added `use_sim_time: True` to `robot_state_publisher` parameters in the launch file.

```python
# Added use_sim_time argument and passed to node
DeclareLaunchArgument(
    'use_sim_time',
    default_value='true',
    description='Use simulation (Gazebo) clock if true'
),
Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher',
    output='screen',
    parameters=[robot_description, {'use_sim_time': use_sim_time}]
)
```

---

### 9. `testbed_description/urdf/testbed.gazebo`: Caster Friction Causing Severe Odometry Drift
- **Symptom:** As soon as the robot rotated or turned, it skidded sideways across the floor. The wheel odometry (`/odom`) drifted significantly from the actual Gazebo pose, causing AMCL localization to fail.
- **Cause:** The 4 caster wheels are modeled as `<joint type="fixed">` joints. In `testbed.gazebo`, their friction was set to `mu1=0.2, mu2=0.2`, while the drive wheels also had low friction (`0.2`). The fixed casters acted like brake pads dragging along the floor, inducing slip on the drive wheels.
- **Fix:** Set caster friction to `mu1=0.0, mu2=0.0` (frictionless sliding contact) and increased drive wheel friction to `mu1=1.0, mu2=1.0` for solid traction.

```xml
<!-- Casters: frictionless sliding -->
<gazebo reference="caster_1">
  <material>${body_color}</material>
  <mu1>0.0</mu1>
  <mu2>0.0</mu2>
  <self_collide>true</self_collide>
</gazebo>

<!-- Drive wheels: good traction -->
<gazebo reference="right_wheel_1">
  <material>${body_color}</material>
  <mu1>1.0</mu1>
  <mu2>1.0</mu2>
  <self_collide>true</self_collide>
</gazebo>
```

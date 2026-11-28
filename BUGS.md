# Bugs found in the starter code and how they were fixed

Defects found in the provided `testbed_description`, `testbed_gazebo` and `testbed_bringup`
packages, with evidence, root cause and fix for each.

## How the bugs were found

1. Built and ran the untouched starter code on ROS 2 Humble (Gazebo 11): `colcon build`, then, with
   only bug 1 patched, `map_server` on the shipped map and the robot in a headless
   `gzserver --verbose`. This surfaced bugs 1, 2, 3, 5, 6 and 7 (output below).
2. Read every launch, CMake, `package.xml`, xacro and Gazebo file.
3. Measured the STL meshes with a small binary-STL parser (bounding boxes, mm → m). The meshes use
   CAD coordinates (the base_link frame), so their bounds give the wheel positions, track width and
   sensor locations to compare with the joint, visual and inertial origins in the URDF.

Output from the untouched starter code:

```text
$ colcon build
Starting >>> testbed_description
Starting >>> testbed_bringup
CMake Error at CMakeLists.txt:24:
  Parse error.  Expected "(", got newline with text "
  ".
Failed   <<< testbed_description [0.10s, exited with code 1]
Aborted  <<< testbed_bringup [1.81s]
Summary: 0 packages finished [2.05s]
  1 package failed: testbed_description
# after patching only ament_package(): installed share dirs, map_server configure, gzserver --verbose with the robot
$ ls install/testbed_bringup/share/testbed_bringup  ->  cmake environment hook launch   (no maps/)
$ ls install/testbed_gazebo/share/testbed_gazebo    ->  cmake environment hook launch worlds   (no models/)
[ERROR] [map_io]: Failed to load image file .../maps/wrong_path_testbed_world.pgm for reason: Magick: Unable to open file (...)
[ERROR] [map_server]: Original error: Failed to load map yaml file: .../maps/testbed_world.yaml
[Err] [Plugin.hh:212] Failed to load plugin libgazebo_ros_control.so: libgazebo_ros_control.so: cannot open shared object file: No such file or directory
$ ros2 topic info /joint_states  ->  Publisher count: 0      $ ros2 topic echo /scan --once --field range_max  ->  1.5
```

The other bugs log no errors. Bugs 4, 13, 14 and 15 were found by reading the files, bugs 9–12 by
measuring the meshes, and bug 8 by measuring the running simulation against Gazebo's ground-truth pose.

## At a glance

15 bugs fixed across 3 packages (plus one repo-level file).

| By severity                         | Count | Bugs                 |
| ----------------------------------- | :---: | -------------------- |
| Critical: build or map load fails   |   3   | 1, 2, 3              |
| High: localization fails            |   1   | 5                    |
| Medium: wrong or inconsistent       |   6   | 4, 7, 8, 9, 10, 11   |
| Low: logs, visuals, packaging       |   5   | 6, 12, 13, 14, 15    |

| By area                             | Count | Bugs                 |
| ----------------------------------- | :---: | -------------------- |
| Build, install and packaging        |   3   | 1, 3, 13             |
| Launch files and map config         |   3   | 2, 4, 14             |
| Gazebo plugins and sensors          |   4   | 5, 6, 7, 10          |
| Robot model and physics             |   4   | 8, 9, 11, 12         |
| Housekeeping                        |   1   | 15                   |

| By package                          | Count | Bugs                 |
| ----------------------------------- | :---: | -------------------- |
| `testbed_description`               |  10   | 1, 5–7, 9–12, 14, 15 |
| `testbed_bringup`                   |   1   | 2                    |
| Several packages                    |   4   | 3, 4, 8, 13          |

| By evidence                         | Count | Bugs                 |
| ----------------------------------- | :---: | -------------------- |
| Error or wrong value in real output |   7   | 1, 2, 3, 5, 6, 7, 8  |
| Measured from the meshes            |   4   | 9–12                 |
| Found by reading the files          |   4   | 4, 13, 14, 15        |

## Summary

| #   | File(s)                                                                                     | Symptom                                                                         | Fix                                                                              |
| --- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 1   | `testbed_description/CMakeLists.txt`                                                        | Whole workspace fails to configure                                              | `ament_package` → `ament_package()`                                              |
| 2   | `testbed_bringup/maps/testbed_world.yaml`                                                   | map_server cannot load the map                                                  | `image: testbed_world.pgm`                                                       |
| 3   | `testbed_bringup/CMakeLists.txt`, `testbed_gazebo/CMakeLists.txt`                           | `maps/` and `models/` missing from `install/`                                   | Added to `install(DIRECTORY ...)`                                                |
| 4   | `testbed_description/launch/robot_description.launch.py`                                    | Runs on wall-clock time while the rest of the simulation uses `/clock`          | `use_sim_time` argument (default `true`), `ParameterValue(..., value_type=str)`  |
| 5   | `testbed_description/urdf/testbed.gazebo`                                                   | Lidar sees almost nothing (1.5 m range in a 20 m × 20 m world)                  | Range 0.12–12.0 m, 360 samples                                                   |
| 6   | `testbed_description/urdf/testbed.gazebo`                                                   | `libgazebo_ros_control.so` fails to load (ROS 1 plugin)                         | Plugin removed                                                                   |
| 7   | `testbed_description/urdf/testbed.gazebo`                                                   | Nothing publishes `/joint_states`; wheel TF comes from the drive plugin instead | Added `gazebo_ros_joint_state_publisher`; `publish_wheel_tf` → `false`           |
| 8   | `testbed_description/urdf/testbed.gazebo`, `testbed_gazebo/worlds/testbed_playground.world` | Idle robot creeps and turns by itself                                           | Solver iterations 50 → 200; wheels μ = 1.0 with a stiff contact; casters μ = 0.0 |
| 9   | `testbed_description/urdf/testbed.xacro`                                                    | `base_footprint` is not at the drive-axle center                                | `fixed_base_joint` origin `0.0505 0.0378 0`; empty `base_footprint` link         |
| 10  | `testbed_description/urdf/testbed.gazebo`                                                   | Wrong `wheel_separation`: robot turns ~7 % less than commanded                  | 0.35 → 0.376 m; added torque/acceleration limits                                 |
| 11  | `testbed_description/urdf/testbed.xacro`                                                    | Centres of mass 23–36 cm outside the robot                                      | Inertial origins set from the measured meshes                                    |
| 12  | `testbed_description/urdf/testbed.xacro`                                                    | IMU and dummy meshes drawn at each other's frames; hand-edited visual offsets   | Mesh files swapped; visual origins = −(joint origin)                             |
| 13  | `*/package.xml`                                                                             | Missing run dependencies, so `rosdep` and clean installs fail                   | Added `exec_depend`s and descriptions                                            |
| 14  | `testbed_description/launch/testbed_rviz_barebones.launch.py`                               | `use_sim_time: True` with no Gazebo, so no `/clock`                             | `use_sim_time: False`; `ParameterValue` for the URDF                             |
| 15  | `testbed.gazebo`, `.vscode/settings.json`                                                   | Stray `>` in the IMU plugin; hard-coded `/home/eric-ros1` path                  | `>` removed; `.vscode/` removed                                                  |

---

## 1. `ament_package` called without parentheses

- File: `testbed_description/CMakeLists.txt`
- Evidence: `colcon build` fails configuring `testbed_description` with
  `CMake Error at CMakeLists.txt:24: Parse error.  Expected "(", got newline` (end of file) and
  aborts the packages still building, so the build finishes 0 packages.
- Root cause: CMake commands need a parenthesized argument list; a bare `ament_package` is a syntax error.
- Fix: `ament_package` → `ament_package()`
- Why: `ament_package()` generates the package's CMake config and its ament resource-index entry,
  which `FindPackageShare` / `get_package_share_directory` need to find the package.

## 2. Wrong image path in the map YAML

- File: `testbed_bringup/maps/testbed_world.yaml`
- Evidence: `map_server` fails to configure (`Failed to load image file
  .../wrong_path_testbed_world.pgm`, then `Failed to load map yaml file`), stays `unconfigured` and
  publishes no `/map`.
- Root cause: The YAML sets `image: wrong_path_testbed_world.pgm`; the file is `testbed_world.pgm`.
- Fix: `image: wrong_path_testbed_world.pgm` → `image: testbed_world.pgm`
- Why: `map_server` resolves a relative `image` path against the YAML file's directory, so a bare
  filename is portable.

## 3. Map and Gazebo models are not installed

- Files: `testbed_bringup/CMakeLists.txt`, `testbed_gazebo/CMakeLists.txt`
- Evidence: After `colcon build`, `install/testbed_bringup/share/testbed_bringup/maps/`
  and `install/testbed_gazebo/share/testbed_gazebo/models/` do not exist, yet
  `spawn_playground.launch.py` adds `share/testbed_gazebo/models` to `GAZEBO_MODEL_PATH`, and launch
  files that load the map through `get_package_share_directory('testbed_bringup')` fail.
- Root cause: `install(DIRECTORY ...)` lists only `launch` (bringup) and `launch worlds` (gazebo).
- Fix:
  ```cmake
  # testbed_bringup
  install(DIRECTORY launch maps DESTINATION share/${PROJECT_NAME}/)
  # testbed_gazebo
  install(DIRECTORY launch worlds models DESTINATION share/${PROJECT_NAME}/)
  ```
- Why: At runtime, ROS 2 resolves packages from the install space, so uninstalled files are
  unavailable to launch files. Builds with `--symlink-install` hide this bug.

## 4. `robot_state_publisher` does not use simulation time

- File: `testbed_description/launch/robot_description.launch.py` (and the include in
  `testbed_bringup/launch/testbed_full_bringup.launch.py`)
- Evidence: Gazebo publishes `/clock` and the other simulation nodes (RViz, later AMCL and Nav2) run
  with `use_sim_time: true`, but `robot_state_publisher` reports `use_sim_time: False` and stamps
  `/tf_static` with wall-clock time (about 1.8 × 10⁹ s) while `/clock` reads about 194 s. As shipped
  this causes no error, since static transforms ignore their stamps and the wheel TF comes from the
  diff-drive plugin. Once `/joint_states` exists (bug 7), TF for the moving joints would carry the
  wrong clock.
- Root cause: `robot_state_publisher` receives no `use_sim_time` parameter.
- Fix:
  - Added a `use_sim_time` launch argument (default `true`), passed to the node as
    `{'use_sim_time': use_sim_time}`. `testbed_full_bringup.launch.py` passes `use_sim_time: 'true'`
    explicitly to the include.
  - Wrapped the xacro `Command` in `ParameterValue(..., value_type=str)`.
- Why: Nodes that exchange time-stamped data must share one clock. `ParameterValue(value_type=str)`
  stops `launch_ros` from parsing the generated URDF as YAML, which fails on some URDF contents, and
  is the recommended pattern on Humble.

## 5. Lidar range limited to 1.5 m

- File: `testbed_description/urdf/testbed.gazebo` (`lidar_link_1` sensor)
- Evidence: The map covers x ∈ [−10.2, 10.05] m and y ∈ [−9.94, 10.06] m. From the spawn pose (0, 5),
  `range_max` is 1.5 and all 300 of 300 rays return `inf`, so AMCL has nothing to match against the
  map and the costmaps see obstacles only at the last moment.
- Root cause: `<range><min>0.10</min><max>1.5</max>`, with 300 samples.
- Fix: `min 0.10 → 0.12`, `max 1.5 → 12.0`, `samples 300 → 360`. Angle limits unchanged at ±3.14 rad.
- Why: 12 m covers the room from any pose, as a typical 2D indoor lidar does. 360 samples give about
  1° resolution. The 0.12 m minimum starts the rays outside the housing (half-diagonal ≈ 0.064 m),
  so the robot does not see itself. ±3.14 avoids a duplicated beam at ±π.

## 6. ROS 1 `gazebo_ros_control` plugin

- File: `testbed_description/urdf/testbed.gazebo`
- Evidence: gzserver logs `[Err] [Plugin.hh:212] Failed to load plugin libgazebo_ros_control.so:
  libgazebo_ros_control.so: cannot open shared object file: No such file or directory` (on screen with
  `verbose:=true`, otherwise only in `~/.gazebo/server-*/default.log`).
- Root cause: `libgazebo_ros_control.so` is the ROS 1 `gazebo_ros_control` plugin and does not exist
  in ROS 2 Humble. The ROS 2 equivalent, `gazebo_ros2_control`, needs a `<ros2_control>` block and
  controller YAML, which this robot does not use.
- Fix: Removed the plugin block. `libgazebo_ros_diff_drive.so` drives the robot.
- Why: The diff-drive plugin already subscribes to `cmd_vel` and publishes `odom` and the
  `odom → base_footprint` TF, which is all Nav2 needs.

## 7. No `/joint_states` publisher

- File: `testbed_description/urdf/testbed.gazebo`
- Evidence: `left_wheel_joint` and `right_wheel_joint` are `continuous`, but
  `ros2 topic info /joint_states` shows `Publisher count: 0`, so `robot_state_publisher` publishes no
  TF for these joints. The wheel frames exist only because the diff-drive plugin publishes them
  (`publish_wheel_tf: true`), bypassing the URDF. Other `/joint_states` consumers (RViz joint display,
  logging, a future ros2_control setup) get nothing.
- Root cause: The simulation has no joint-state publisher; wheel TF is a side effect of the drive plugin.
- Fix:
  ```xml
  <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
    <update_rate>50</update_rate>
    <joint_name>left_wheel_joint</joint_name>
    <joint_name>right_wheel_joint</joint_name>
  </plugin>
  ```
  and `<publish_wheel_tf>true</publish_wheel_tf>` → `false`.
- Why: Each TF edge should have one publisher. In the standard ROS 2 pipeline, Gazebo reports the
  joint angles and `robot_state_publisher` converts them to TF using the URDF.

## 8. Robot creeps and turns on its own in the simulation

- Files: `testbed_description/urdf/testbed.gazebo` (contact parameters),
  `testbed_gazebo/worlds/testbed_playground.world` (physics solver)
- Evidence: With no velocity command, the untouched starter robot turns by itself
  (yaw −2.18° → −2.46° in 13.6 s of sim time, about 1.2°/min). With the starter's contact values it
  also slides, even with the solver fix below: 1.5 cm in 60 s of idling, and 3.9 cm plus 0.025 rad in
  the 90 s after a short drive. AMCL and the costmaps see a moving robot while Nav2 assumes it is
  stationary.
- Root cause:
  1. Solver iterations. The 0.15 kg wheels carry a body of about 7 kg (the four casters alone are
     4.7 kg). With ODE's default of 50 `quick` iterations, the wheel-motor and contact constraints do
     not converge for that mass ratio. The held wheels creep (measured with `/joint_states`) and the
     robot rolls with them.
  2. Contact values. Every link, drive wheels included, has the placeholder `mu1 = mu2 = 0.2` and
     ODE's default soft contact.
- Fix:
  - World: `<ode><solver><type>quick</type><iters>200</iters></solver></ode>`.
  - Wheels: `mu1 = mu2 = 1.0`, `kp = 1e6`, `kd = 100`, `maxVel = 0.1`. `minDepth` is left unset
    because a 1 mm wheel sink put the weight on the casters, which sit only 0.4 mm higher, and with
    frictionless casters the robot then turned by itself at 0.9 rad/min, worse than the original.
  - Casters (fixed, non-rolling): `mu1 = mu2 = 0.0`, so they slide like ball casters.
- Result, measured against Gazebo's ground-truth pose:

  | Configuration                               | Idle 60 s: yaw / shift | 90 s after a drive: yaw / shift |
  | ------------------------------------------- | ---------------------- | ------------------------------- |
  | Starter contact values, 200 iterations      | 0.0066 rad / 15 mm     | 0.025 rad / 39 mm               |
  | New contact values, 50 iterations (default) | 0.0041 rad / 0.8 mm    | 0.167 rad / 5 mm                |
  | New contact values, 200 iterations (final)  | 0.0005 rad / 0.7 mm    | 0.0002 rad / 1.0 mm             |

  Steady-state tracking with the final values: 0.300 m/s for 0.3 m/s commanded, 0.983 rad/s for
  1.0 rad/s commanded. The starter's friction tracked turns equally well (1.008 rad/s); the problem
  is creep at rest.
- Why: An iterative solver needs more passes when a light body (the wheel) transmits the forces of a
  much heavier one; 200 iterations at a 1 ms step cost little for one robot. Stiff, high-grip wheel
  contacts let the motors hold the robot. Frictionless casters resist no lateral force, so the drive
  wheels must carry the weight.

## 9. `base_footprint` is not at the drive-axle center

- File: `testbed_description/urdf/testbed.xacro` (`fixed_base_joint`, `base_footprint`)
- Evidence: In the base_link frame, the meshes put the left and right wheel tread centers at
  y = +0.1502 and y = −0.2258, both at x = −0.0505, so the drive-axle center is (−0.0505, −0.0378, 0).
  The body mesh center is the same point (−0.0507, −0.0379), so the robot is symmetric about its axle.
  `fixed_base_joint` has origin `0 0 0`, which places `base_footprint` (the frame the diff-drive
  plugin moves, and the robot frame for AMCL and Nav2) at the CAD origin, 6.3 cm from the rotation
  center. In an in-place rotation `base_footprint` traces a circle, the controller's kinematic model
  is wrong, and the footprint polygon is off-center.
- Root cause: The CAD export put base_link's origin at an arbitrary CAD point, and the footprint
  frame was never moved to the axle.
- Fix:
  - `fixed_base_joint` origin `0 0 0` → `0.0505 0.0378 0` (base_link's pose in base_footprint).
  - Replaced the zero-size `<box size="0.0 0.0 0.0" />` visual on `base_footprint` with an empty `<link name="base_footprint"/>`.
- Why: REP-105 and Nav2 expect `base_footprint` at the ground projection of the rotation center, which
  for a differential drive is the drive-axle midpoint. After the fix the wheels sit at y = ±0.188 m and
  the footprint is symmetric (about ±0.175 m × ±0.203 m). A zero-size box is degenerate geometry that
  some tools reject; an empty link is the standard frame-only link.

## 10. Wrong `wheel_separation`

- File: `testbed_description/urdf/testbed.gazebo` (diff-drive plugin)
- Evidence: `wheel_separation` is 0.35, close to the distance between the joint origins (0.346 m),
  which lie on the wheels' inner faces. The tread-center distance from the meshes is
  0.1502 − (−0.2258) = 0.376 m. The plugin uses this value to convert `cmd_vel` angular velocity into
  wheel speeds, so the robot turns 0.35 / 0.376 ≈ 93 % of the commanded rate. In the starter,
  odometry comes from the Gazebo model pose (`odometry_source` default 1), so the error showed only
  as under-rotation. With encoder odometry (now enabled, see below) the same value also integrates
  odometry, and a wrong track would corrupt every heading estimate.
- Root cause: The separation was taken from the joint frames instead of the contact patches.
- Fix: `0.35` → `0.376`. `wheel_diameter` 0.1 is correct (mesh height 0.100 m). Added
  `<max_wheel_torque>20</max_wheel_torque>` and `<max_wheel_acceleration>2.0</max_wheel_acceleration>`.
- Why: For a differential drive, ω = (v_r − v_l) / track, so a wrong track scales every commanded and
  estimated rotation. The limits prevent unbounded torque when Nav2 sends velocity steps.

## 11. Bogus inertial origins

- File: `testbed_description/urdf/testbed.xacro`
- Evidence: The inertial origins, expressed in each link's own frame, lie far outside the link's mesh:

  | link           | inertial origin (before)    | distance from mesh center |
  | -------------- | --------------------------- | ------------------------- |
  | `lidar_link_1` | (−0.0457, −0.2128, −0.0690) | 22.6 cm                   |
  | `imu_link_1`   | (−0.2157, −0.3448, −0.0820) | 29.0 cm                   |
  | `dummy_link_1` | (−0.2157, −0.0848, −0.0820) | 35.8 cm                   |

  Gazebo merges fixed-joint links into one body, so these masses shift the robot's center of mass
  sideways and bias its contact forces.
- Root cause: The values look like CAD-frame coordinates pasted into link frames.
- Fix: Each inertial origin is now the mesh bounding-box center minus the joint origin, a good
  center-of-mass estimate for these small, near-box parts.

  | link           | after                      |
  | -------------- | -------------------------- |
  | `lidar_link_1` | (−0.0057, 0.0022, 0.0095)  |
  | `imu_link_1`   | (0.0043, −0.0038, −0.0035) |
  | `dummy_link_1` | (0.0043, 0.0077, −0.0035)  |
- Why: `<inertial><origin>` is the center of mass in the link frame. Correct placement keeps the
  merged center of mass inside the support polygon and the wheel loads balanced.

## 12. IMU and dummy meshes swapped; hand-edited visual offsets

- File: `testbed_description/urdf/testbed.xacro`
- Evidence: In this CAD export a correct link has visual origin = −(joint origin), which renders its
  mesh at the CAD position. Measured:
  - The `imu_link_1` frame is at y = +0.05 but renders `imu_link_1.stl`, whose box is at y = −0.124
    (17 cm away).
  - The `dummy_link_1` frame is at y = −0.1315 but renders `dummy_link_1.stl`, whose box is at
    y = +0.046 (18 cm away).
  - The dummy visual y is 0.14 instead of 0.1315 and the lidar visual y is 0.033 instead of 0.04.
    The visual z offsets are −0.226509 (lidar) and −0.1612 (IMU, dummy) instead of −0.228 / −0.163.

  RViz therefore draws the IMU away from the frame its data is reported in.
- Root cause: Mesh filenames swapped between the two links, plus hand-edited visual offsets.
- Fix: Swapped the `<mesh filename>` between `imu_link_1` and `dummy_link_1`, and set the visual and
  collision origins to exactly −(joint origin): lidar `0.04 0.04 -0.228`, IMU `0.1 -0.05 -0.163`,
  dummy `0.1 0.1315 -0.163`. Every sensor frame is now within about 1 cm of its mesh (IMU 0.67 cm,
  dummy 0.95 cm, lidar 1.13 cm, mostly because the scan-plane frame sits 0.95 cm below the center of
  the housing's bounding box).
- Why: `/imu` and `/scan` are stamped with the sensor frame, so a model that draws the hardware
  elsewhere makes visual debugging misleading. The two meshes are identical boxes, so swapping the
  filenames is the minimal exact fix.

## 13. Missing run dependencies in `package.xml`

- Files: `testbed_description/package.xml`, `testbed_gazebo/package.xml`, `testbed_bringup/package.xml`
- Evidence: The launch files use `xacro`, `robot_state_publisher`, `joint_state_publisher`, `rviz2`,
  `gazebo_ros` (`spawn_entity.py`, `gazebo.launch.py`), Gazebo plugins (`gazebo_plugins`) and
  `launch_ros`. On a fresh machine `rosdep install --from-paths src` does not install them, and the
  launches fail with package-not-found errors.
- Root cause: None of these are declared. `testbed_bringup` also calls `find_package(rclpy)` without
  declaring `rclpy`.
- Fix: Added `exec_depend`s:
  - `testbed_description`: `xacro`, `robot_state_publisher`, `joint_state_publisher`, `rviz2`, `launch`, `launch_ros`
  - `testbed_gazebo`: `gazebo_ros`, `gazebo_plugins`, `launch`, `launch_ros`
  - `testbed_bringup`: `build_depend rclpy`, `exec_depend` `testbed_description`, `testbed_gazebo`, `rviz2`, `launch`, `launch_ros`

  Also replaced the `TODO` descriptions with real ones.
- Why: `rosdep`, colcon's build ordering and binary packaging all read dependencies from
  `package.xml`, so it must declare everything the package uses.

## 14. Barebones RViz launch uses sim time without a simulator

- File: `testbed_description/launch/testbed_rviz_barebones.launch.py`
- Evidence: This launch shows the URDF with `joint_state_publisher` and RViz, without Gazebo, but
  runs `robot_state_publisher` and RViz with `use_sim_time: True`. With no `/clock` publisher, ROS
  time in those nodes stays at 0 while `joint_state_publisher` stamps the joint states with
  wall-clock time. Reproduced without RViz: `robot_state_publisher` `use_sim_time: True`,
  `joint_state_publisher` `False`, `/joint_states` stamped in wall time. No TF rejection was
  observed, but the configuration is inconsistent.
- Root cause: Parameters copied from the simulation launch.
- Fix: `use_sim_time: True` → `False` for both nodes. Also wrapped the URDF `Command` in
  `ParameterValue(..., value_type=str)`, as in bug 4.
- Why: `use_sim_time` should be true only when something publishes `/clock`.

## 15. Minor issues

- Stray `>`: `<initial_orientation_as_reference>false</initial_orientation_as_reference>>` in
  `testbed.gazebo` leaves a literal `>` text node inside the IMU `<plugin>`. Removed.
- Hard-coded developer path: `.vscode/settings.json` contains
  `"cmake.sourceDirectory": "/home/eric-ros1/level01_ros_assignment/testbed_bringup"`, a
  machine-specific path that does not exist on other machines. Removed the `.vscode/` directory.

## Noted, intentionally not changed

- `testbed.trans` declares ROS 1–style `transmission` blocks. They are ignored without
  `ros2_control`, so they are harmless, and they were kept to minimize the diff.
- `testbed_description/rviz/urdf_gazebo.rviz` references `/box_bot/...` topics from a template.
  No launch file uses it.
- Odometry: the starter's diff-drive plugin uses the default `odometry_source` 1, which reports the
  Gazebo model pose (ground truth). This is not a defect, but it hides odometry drift. The
  submission switches to encoder odometry (`odometry_source` 0) fused with the IMU in a
  robot_localization EKF; see `testbed_navigation/README.md`, Odometry.
- `full_bringup.rviz` uses fixed frame `odom` and has no map display. That suits the raw simulation
  bringup, so navigation uses its own config in `testbed_navigation/rviz/`.

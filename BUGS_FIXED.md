# Bugs found in the starter code and how they were fixed

Each entry gives the file, the symptom (how it was found), and the fix.

| # | Package / file | Bug | Fix |
|---|----------------|-----|-----|
| 1 | `testbed_description/CMakeLists.txt` | `ament_package` is written without `()`. `colcon build` fails: *CMake Error: Parse error. Expected "(", got newline*. | Changed it to `ament_package()`. |
| 2 | `testbed_bringup/maps/testbed_world.yaml` | `image: wrong_path_testbed_world.pgm`. That file does not exist, so `map_server` cannot load the map. | Changed it to `image: testbed_world.pgm`. The path is relative to the yaml file. |
| 3 | `testbed_bringup/CMakeLists.txt` | Only `launch/` is installed. `maps/` never reaches `install/share/testbed_bringup`, so `get_package_share_directory('testbed_bringup')/maps/...` fails. | Added `maps` to the `install(DIRECTORY ...)` list. |
| 4 | `testbed_gazebo/CMakeLists.txt` | `models/` is not installed. `spawn_playground.launch.py` adds `share/testbed_gazebo/models` to `GAZEBO_MODEL_PATH`, but that folder does not exist. | Added `models` to the `install(DIRECTORY ...)` list. |
| 5 | `testbed_description/launch/robot_description.launch.py` | `robot_state_publisher` runs without `use_sim_time`. `ros2 param get /robot_state_publisher use_sim_time` returned `False`, so its TFs are stamped with wall-clock time while Gazebo and Nav2 use `/clock`. This causes TF extrapolation errors. | Added `{'use_sim_time': True}`. The xacro output is also wrapped in `ParameterValue(..., value_type=str)`, which is the robust way to pass `robot_description`. |
| 6 | `testbed_description/urdf/testbed.gazebo` | It loads `libgazebo_ros_control.so`, which is a ROS 1 plugin and doesn't exist in ROS 2 Humble. | Removed the plugin. The `gazebo_ros_diff_drive` plugin already drives the robot. |
| 7 | `testbed_description/urdf/testbed.gazebo` | No node publishes `/joint_states` for the two continuous wheel joints, so `robot_state_publisher` cannot publish `left_wheel_1` and `right_wheel_1`, and RViz shows the wheels with "No transform". `publish_wheel_tf` in the diff-drive plugin publishes frames named after the *joints* (`left_wheel_joint`), not the links. | Added the `libgazebo_ros_joint_state_publisher.so` plugin for both wheel joints and set `publish_wheel_tf` to `false`. The wheel TFs now come from `robot_state_publisher`. |
| 8 | `testbed_description/urdf/testbed.gazebo` | `wheel_separation` is `0.35`. In the URDF and meshes, the wheel centres are at y = +0.150 and y = −0.226 (base_link frame), so the real separation is **0.376 m**. The wrong value makes commanded turn rates about 7 % off. | Set `wheel_separation` to `0.376`. The diameter of 0.1 m was checked and is correct. |
| 9 | `testbed_description/urdf/testbed.xacro` | `base_footprint` coincides with `base_link`, which is not the robot's rotation centre. From the meshes, the wheel axle centre is at (−0.0505, −0.0378) in `base_link`. Nav2 controllers and the costmap footprint assume the base frame is the rotation centre, so the robot swept a circle when turning in place. | Moved `fixed_base_joint` to `xyz="0.0505 0.0378 0"`. `base_footprint` is now on the axle centre and the footprint becomes symmetric: x ∈ [−0.175, 0.175], y ∈ [−0.203, 0.203]. |
| 10 | `testbed_description/urdf/testbed.gazebo` (lidar) | Max lidar range is **1.5 m**. The map is 20 m × 20 m with large open areas, so most beams return nothing and AMCL cannot localize. | Raised `<range><max>` to `12.0` m. |
| 11 | `testbed_description/urdf/testbed.gazebo` (sensor / odometry rates) | The lidar ran at 30 Hz and the diff-drive odometry/TF at 100 Hz, more than a 2D navigation robot needs. That extra load on every TF listener made the tf2 deadlock described below happen sooner. | Set the lidar `update_rate` to 10 Hz and the diff-drive `update_rate` to 30 Hz. These are typical values for a small differential-drive robot, the same as the TurtleBot3 Nav2 demo. The wheel `joint_state_publisher` also runs at 10 Hz. |
| 12 | `testbed_description/urdf/testbed.gazebo` (IMU) | Typo `</initial_orientation_as_reference>>`, which leaves a stray `>` in the SDF. | Removed the extra `>`. |
| 13 | `package.xml` of `testbed_description`, `testbed_gazebo`, `testbed_bringup` | Run-time dependencies are missing (`xacro`, `robot_state_publisher`, `gazebo_ros`, `testbed_gazebo`, `rviz2`, ...), so `rosdep install` cannot set up a fresh machine. | Added the matching `<exec_depend>` entries. |

### Not a starter-code bug: tf2 deadlock in ROS 2 Humble (worked around in `testbed_navigation`)

At first, the costmaps were fed live `/scan` data through the costmap `ObstacleLayer`. With that setup, the costmap robot pose froze after one to several minutes of driving, faster under load such as the Gazebo GUI, RViz and screen recording. Goals then failed with *"Controller patience exceeded"*, *"Resulting plan has 0 poses in it"* or *"Pose Goes Off Grid"*.

To find the cause, `controller_server` was run under `gdb` and interrupted while frozen. Two threads were deadlocked inside `tf2_ros`:

* **Laser subscription thread:** `ObstacleLayer` → `tf2_ros::MessageFilter::add` → `tf2_ros::Buffer::waitForTransform` (holding the buffer's timer mutex) → `tf2::BufferCore::addTransformableRequest`, waiting for the *request* mutex.
* **TF listener thread:** `TransformListener::subscription_callback` → `BufferCore::setTransform` → `testTransformableRequests` (holding the *request* mutex) → the callback lambda in `buffer.cpp:219`, waiting for the *timer* mutex.

The TF listener never resumes, so the costmap's TF buffer stops updating. This is a lock-order bug in tf2_ros 0.25.x and cannot be fixed with parameters.

**Workaround:** both costmaps use `StaticLayer` + `InflationLayer`, which avoids the MessageFilter path. Live lidar safety is handled by `collision_monitor`, which reads `/scan` directly. With this change and Cyclone DDS (recommended by `help.md`, because Fast DDS sometimes lost lifecycle service replies at start-up), every stress test passed: Gazebo GUI, both RViz windows and screen recording running together, with 3- and 6-goal routes.

### Noticed but not changed

* `.vscode/settings.json` hard-codes `/home/eric-ros1/...`, a path on the original author's machine. It is editor-only and has no effect on the build.
* The `imu_joint` and `dummy_joint` origins seem swapped relative to their meshes. The IMU frame sits at y = +0.05, but the IMU mesh is at y ≈ −0.12. Neither frame is used for navigation, so they were left as they are.

## How the bugs were found

1. `colcon build`, which found #1.
2. Ran `testbed_full_bringup.launch.py` and checked `ros2 topic list`, `ros2 param get`, `tf2_echo` and the Gazebo log, which found #5–#7 and #12.
3. Measured the mesh bounding boxes from the STL files and compared them with the joint origins, which found #8 and #9.
4. Loaded the map and overlaid a live `/scan` on it using the ground-truth pose. 283 of 298 beams hit map walls with no correction, so the map and the world are aligned. Then checked the sensor configuration against the map size, which found #2–#4 and #10.
5. Tested the full Nav2 stack end to end with goals, which found #11.

# Robot Architecture & System Specifications

**Repository:** `level01_ros_assignment`  
**Target Environment:** ROS 2 Humble / Gazebo Classic 11.10.2 / Ubuntu 22.04  
**Robot Platform:** Testbed-T1.0.0 (Two-wheel differential drive with four passive casters)

---

## 1. Frame Architecture & TF Tree

| Item | Frame Name | Defined In | Notes |
| :--- | :--- | :--- | :--- |
| **Robot Footprint Frame** | `base_footprint` | `testbed.xacro` (L9-L16) | Ground-level projection of the robot base. Used as `robot_base_frame` in diff-drive plugin. |
| **Robot Base Frame** | `base_link` | `testbed.xacro` (L18-L37) | Structural chassis frame, connected to `base_footprint` via fixed joint `fixed_base_joint` at `(0, 0, 0)`. |
| **Odometry Frame** | `odom` | `testbed.gazebo` (L27) | Published by Gazebo diff-drive plugin `libgazebo_ros_diff_drive.so`. |
| **Map Frame** | `map` | ROS 2 Nav2 standard | Global fixed frame. Published by AMCL (`nav2_amcl`) as the `map` -> `odom` transform. |
| **LiDAR Frame** | `lidar_link_1` | `testbed.xacro` (L144, L265) | Rigidly attached to `base_link` via `lidar_joint` at `(-0.04, -0.04, 0.228)` meters. |
| **IMU Frame** | `imu_link_1` | `testbed.xacro` (L165, L271) | Rigidly attached to `base_link` via `imu_joint` at `(-0.1, 0.05, 0.163)` meters. |
| **Wheel Frames** | `left_wheel_1`, `right_wheel_1` | `testbed.xacro` | Continuous joints attached to `base_link` along Y axis. |
| **Caster Frames** | `caster_1`, `caster_2`, `caster_3`, `caster_4` | `testbed.xacro` | Four passive casters attached via fixed joints to `base_link`. |

### TF Tree Hierarchy

```text
map
 └── odom                      [Published by: nav2_amcl]
      └── base_footprint       [Published by: libgazebo_ros_diff_drive]
           ├── base_link       [Published by: robot_state_publisher via fixed_base_joint]
           │    ├── caster_1   [Published by: robot_state_publisher]
           │    ├── caster_2   [Published by: robot_state_publisher]
           │    ├── caster_3   [Published by: robot_state_publisher]
           │    ├── caster_4   [Published by: robot_state_publisher]
           │    ├── dummy_link_1 [Published by: robot_state_publisher]
           │    ├── imu_link_1 [Published by: robot_state_publisher]
           │    └── lidar_link_1 [Published by: robot_state_publisher]
           ├── left_wheel_1    [Published by: libgazebo_ros_diff_drive or joint_state_publisher]
           └── right_wheel_1   [Published by: libgazebo_ros_diff_drive or joint_state_publisher]
```

---

## 2. Topics & Message Interfaces

| Function | Topic Name | Message Type | Publisher | Subscriber(s) |
| :--- | :--- | :--- | :--- | :--- |
| **LiDAR Scans** | `/scan` | `sensor_msgs/msg/LaserScan` | Gazebo Ray Sensor (`libgazebo_ros_ray_sensor.so`) | AMCL, Nav2 Local & Global Costmaps, RViz |
| **Odometry** | `/odom` | `nav_msgs/msg/Odometry` | Gazebo Diff Drive (`libgazebo_ros_diff_drive.so`) | Nav2 Controller, AMCL, RViz |
| **Velocity Commands** | `/cmd_vel` | `geometry_msgs/msg/Twist` | Nav2 Controller Server / Teleop | Gazebo Diff Drive (`libgazebo_ros_diff_drive.so`) |
| **Robot Description** | `/robot_description` | `std_msgs/msg/String` | `robot_state_publisher` | Gazebo Spawner, RViz |
| **Global Map** | `/map` | `nav_msgs/msg/OccupancyGrid` | `nav2_map_server` | AMCL, Nav2 Global Costmap, RViz |
| **Initial Pose** | `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz 2D Pose Estimate tool | AMCL (`nav2_amcl`) |
| **Goal Pose** | `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz Nav2 Goal tool | Nav2 BT Navigator action server |
| **IMU** | `/imu` | `sensor_msgs/msg/Imu` | Gazebo IMU Sensor (`libgazebo_ros_imu_sensor.so`) | Sensor fusion / diagnostics |

---

## 3. Actuation & Drive Specifications

- **Controller Type:** Differential Drive via Gazebo plugin `libgazebo_ros_diff_drive.so`.
- **Wheel Separation:** 0.35 m (actual URDF joint offsets: Left Y = +0.135241 m, Right Y = -0.210759 m -> span = 0.346 m).
- **Wheel Diameter:** 0.1 m (wheel radius = 0.05 m).
- **Update Rate:** 100 Hz.
- **Odometry Publishing:** Enabled (`publish_odom: true`, `publish_odom_tf: true`, `publish_wheel_tf: true`).
- **Command Topic:** `cmd_vel`.
- **Legacy Incompatibility:** `testbed.gazebo` also includes `<plugin name="control" filename="libgazebo_ros_control.so"/>` which is a ROS 1 Gazebo control plugin and invalid in ROS 2.

---

## 4. Sensor Specifications

### LiDAR Sensor
- **Plugin:** `libgazebo_ros_ray_sensor.so` on `lidar_link_1`.
- **Topic:** `/scan` (`sensor_msgs/msg/LaserScan`).
- **Update Rate:** 30 Hz.
- **Field of View:** Horizontal -3.14 to +3.14 rad (360 degrees), 300 samples.
- **Range (in starter code):** Min 0.10 m, Max 1.5 m.
  > **Crucial Observation:** A max range of 1.5 m is insufficient for the 20m x 20m playground world (spawn position is >3.3 m from nearest wall). This will prevent AMCL from localizing and costmaps from detecting obstacles at standard distances. Standard ranges are 8.0 m - 12.0 m.
- **Noise:** Gaussian (stddev: 0.01).

### IMU Sensor
- **Plugin:** `libgazebo_ros_imu_sensor.so` on `imu_link_1`.
- **Topic:** `/imu` (`sensor_msgs/msg/Imu`).
- **Update Rate:** 10 Hz.
- **Syntax defect in starter code:** Line 40 has an extra closing angle bracket: `<initial_orientation_as_reference>false</initial_orientation_as_reference>>`.

---

## 5. Gazebo Simulation & World Configuration

- **World File:** `testbed_gazebo/worlds/testbed_playground.world`
  - Indoor enclosed environment (~20m x 20m) with perimeter brick walls, internal rooms, fences, and obstacles.
- **Models:** Stored in `testbed_gazebo/models/` (`test_room`, `box_room`, `wooden_fence`, `Fence1`, `eric`, `my_world`).
- **Spawn Position:** Configured in `testbed_gazebo/launch/spawn_testbed.launch.py`:
  - `X = 0.0, Y = 5.0, Z = 0.0`
  - Orientation: `Roll = 0.0, Pitch = 0.0, Yaw = 0.0`
  - Spawner: `gazebo_ros/spawn_entity.py` taking description from `/robot_description`.

---

## 6. Predefined Map Configuration

- **YAML File:** `testbed_bringup/maps/testbed_world.yaml`
- **PGM File:** `testbed_bringup/maps/testbed_world.pgm`
- **Dimensions:** 405 x 400 pixels.
- **Resolution:** 0.05 meters/pixel (Ground footprint: 20.25 m x 20.00 m).
- **Origin:** `[-10.2, -9.94, 0.0]`
- **Mode:** `trinary`
- **Occupied Threshold:** 0.65
- **Free Threshold:** 0.25
- **Image defect in starter code:** Line 1 refers to `image: wrong_path_testbed_world.pgm` instead of `testbed_world.pgm`.

---

## 7. Package Dependencies & Build Configuration

- `testbed_description`: URDF, Xacro, meshes, RViz configurations.
  - Defect in `CMakeLists.txt`: Line 23 has `ament_package` instead of `ament_package()`, failing compilation immediately.
  - Launch file `robot_description.launch.py` lacks `use_sim_time` configuration for `robot_state_publisher`.
- `testbed_gazebo`: Gazebo world files, models, and spawn launch files.
  - Defect in `CMakeLists.txt`: `models` directory is not installed in the CMake install directive.
- `testbed_bringup`: Top-level bringup launch files and maps.
  - Defect in `CMakeLists.txt`: `maps` directory is not installed in the CMake install directive.


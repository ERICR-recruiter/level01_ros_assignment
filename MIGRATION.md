# Porting from Humble / Gazebo Classic to Jazzy / Gazebo Harmonic

The assignment was written for **ROS 2 Humble + Gazebo Classic**, while I was working on **Ubuntu 24.04 + ROS 2 Jazzy**. Instead of using the Docker setup suggested in the assignment, I decided to port the existing codebase to Jazzy so I could run and debug it natively.

The original code also had some bugs, which are documented separately in [`BUGS.md`](BUGS.md).

I tested the migrated setup with Gazebo, localization and Nav2 navigation.

## Main changes

### 1. Gazebo Classic → Gazebo Harmonic

Gazebo Classic plugins are not used in Harmonic, so the Gazebo plugins in the robot description had to be changed.

For example:

```text
Gazebo Classic                         Gazebo Harmonic

libgazebo_ros_diff_drive.so       →    gz-sim-diff-drive-system
libgazebo_ros_imu_sensor.so       →    gz-sim-imu-system
libgazebo_ros_ray_sensor.so       →    gz-sim-sensors-system
```

I also added the Gazebo joint state publisher because the Harmonic diff-drive system does not publish joint states in the same way as the old Classic plugin.

The diff-drive parameter names also changed between the two versions, so these had to be updated in the robot configuration.

---

### 2. Sensors

The lidar configuration had to be updated for the Harmonic sensor format.

I also added the appropriate `gz_frame_id` values so that the ROS topics use the expected TF frame names.

The lidar and IMU are now handled by the Gazebo world-level sensor systems.

---

### 3. World files

The world files were updated to the newer SDF format.

Some Classic-specific elements were removed or replaced, including:

* Classic material references
* Recorded GUI state
* Classic model references such as `model://sun`
* Classic physics configuration

The required Gazebo Harmonic world systems were also added.

---

### 4. Launch files

The old `gazebo_ros` launch and spawn commands were replaced with `ros_gz_sim`.

For example:

```text
gazebo_ros spawn_entity.py
            ↓
ros_gz_sim create
```

The world is also passed through `gz_args` when starting Gazebo.

The old Gazebo environment variables were replaced with:

```text
GZ_SIM_RESOURCE_PATH
```

---

### 5. ROS-Gazebo bridge

Gazebo Harmonic communicates using Gazebo Transport, so the required topics have to be bridged to ROS2.

The main topics I bridged were:

```text
/clock
/cmd_vel
/odom
/tf
/joint_states
/imu
/scan
```

This was one of the main differences from the Classic setup, where the Gazebo ROS plugins published ROS messages directly.

For Jazzy, Nav2 was publishing `geometry_msgs/Twist` for `cmd_vel`, so I used the corresponding bridge type.


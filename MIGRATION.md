# Porting the testbed from Humble / Gazebo Classic to Jazzy / Gazebo Harmonic

The assignment targets ROS 2 Humble on Ubuntu 22.04 with Gazebo Classic 11.
I ran it on Ubuntu 24.04, which ships ROS 2 Jazzy, and Jazzy has no Gazebo
Classic — Classic reached end of life in January 2025. The pairing on 24.04 is
Jazzy with Gazebo Harmonic (`gz-sim` 8) through the `ros_gz` bridge packages.

Nothing here is a defect in the starter code; it is the cost of the newer
distro. The actual bugs are in [BUGS.md](BUGS.md).

I did consider the Docker route the FAQ suggests — `osrf/ros:humble-desktop-full`
with the X socket mounted — and it would have worked. I went with the port
instead for two reasons. The starter code does not build as shipped (bug 1), so
a container would not have saved me from touching it anyway, and a port that
runs natively is easier to demo and to debug than a container with display
forwarding in the way.

Verified working end to end: simulation, localization, and a 10 m cross-map
navigation goal with no recovery behaviours triggered.

---

## What changed, and why

### Plugin architecture

Classic loaded shared objects by filename (`libgazebo_ros_diff_drive.so`).
Harmonic loads *systems* by plugin name and registered C++ class. Every plugin
in `testbed.gazebo` had to be re-pointed.

| Classic | Harmonic |
| --- | --- |
| `libgazebo_ros_control.so` | removed — nothing was using it |
| `libgazebo_ros_diff_drive.so` | `gz-sim-diff-drive-system` / `gz::sim::systems::DiffDrive` |
| `libgazebo_ros_imu_sensor.so` | no plugin; `gz-sim-imu-system` runs at world level |
| `libgazebo_ros_ray_sensor.so` | no plugin; `gz-sim-sensors-system` runs at world level |
| — | `gz-sim-joint-state-publisher-system`, newly required |

That last row is the one worth knowing about. Classic's diff-drive plugin
published `/joint_states` itself via `<publish_wheel_tf>`. Harmonic's
`DiffDrive` does not — it only does odometry and the `odom -> base_footprint`
transform. Without adding `JointStatePublisher` explicitly, the wheels never
move in RViz and `robot_state_publisher` has nothing to work from.

The diff-drive parameter names moved as well. `<command_topic>`,
`<odometry_topic>`, `<odometry_frame>`, `<robot_base_frame>` and the
`<publish_*>` flags became `<topic>`, `<odom_topic>`, `<frame_id>`,
`<child_frame_id>` and `<tf_topic>`. `<wheel_diameter>0.1</wheel_diameter>`
became `<wheel_radius>0.05</wheel_radius>` — same wheel, different convention,
and an easy way to end up with a robot that drives at half speed.

All the gz topic names are written absolute (`/scan`, not `scan`). Relative
names get scoped to `/world/<world>/model/<model>/...`, which makes the bridge
configuration depend on the world and model names.

### Sensors

The lidar changed type from `ray` to `gpu_lidar`, and its `<ray>` block became
`<lidar>` with an explicit `<vertical>` section. Both sensors now carry
`<gz_frame_id>` so the bridged messages come out with the right `frame_id`
instead of the simulator's scoped name.

One thing to know when reading the converted SDF: `gz sdf -p` reports both
sensors as children of `base_footprint`, not of `lidar_link_1` and
`imu_link_1`. That is normal — fixed joints are lumped into the canonical link
during URDF-to-SDF conversion, poses are preserved, and `<gz_frame_id>` keeps
the ROS-side frame correct.

### Materials

Classic's `<material>Gazebo/Silver</material>` and the
`file://media/materials/scripts/gazebo.material` script references do not
exist in Harmonic. In the robot I dropped the per-link material overrides
entirely, because the URDF visuals already carry a `silver` material that
converts correctly. In `testbed_playground.world` there were 36 script blocks,
each replaced with explicit `<ambient>` / `<diffuse>` / `<specular>` values.

### World files

- SDF version bumped to 1.10.
- `<physics type='ode'>` became `<physics name='1ms' type='ignored'>`;
  Harmonic selects the physics engine through the plugin, not this attribute.
- Added the world-level systems that Harmonic requires explicitly and Classic
  provided implicitly: `Physics`, `UserCommands`, `SceneBroadcaster`,
  `Sensors`, `Imu`, `Contact`. Without `Sensors` and `Imu` the lidar and IMU
  produce nothing at all, with no error to tell you why.
- Removed the recorded `<state>` block, the `<gui>` camera block and `<audio>`
  — all Classic-only.
- `testbed_empty.world` referenced `model://sun` and `model://ground_plane`,
  which came from Classic's bundled model database. Neither exists in
  Harmonic, so both are defined inline now.

### Launch files and the ROS bridge

`gazebo_ros` is gone. `spawn_playground.launch.py` now includes
`ros_gz_sim/launch/gz_sim.launch.py` and passes the world through `gz_args`
rather than `world`. Spawning moved from `gazebo_ros spawn_entity.py -entity`
to `ros_gz_sim create -name`.

`GAZEBO_MODEL_PATH` and `GAZEBO_PLUGIN_PATH` collapsed into a single
`GZ_SIM_RESOURCE_PATH`, set with `SetEnvironmentVariable` instead of mutating
`os.environ` at launch-description build time.

The part with no Classic equivalent is the bridge. In Classic the plugins were
ROS nodes and published ROS messages directly. Harmonic speaks Gazebo
Transport, so a `ros_gz_bridge` has to be told about every topic:

```
/clock         rosgraph_msgs/msg/Clock     <-  gz.msgs.Clock
/cmd_vel       geometry_msgs/msg/Twist      -> gz.msgs.Twist
/odom          nav_msgs/msg/Odometry       <-  gz.msgs.Odometry
/tf            tf2_msgs/msg/TFMessage      <-  gz.msgs.Pose_V
/joint_states  sensor_msgs/msg/JointState  <-  gz.msgs.Model
/imu           sensor_msgs/msg/Imu         <-  gz.msgs.IMU
/scan          sensor_msgs/msg/LaserScan   <-  gz.msgs.LaserScan
```

The clock bridge lives in `spawn_playground.launch.py` because it belongs to
the world; the rest live in `spawn_testbed.launch.py` because they belong to
the robot.

On `cmd_vel` message types: nav2 1.3.x on Jazzy publishes plain
`geometry_msgs/Twist`, so that is what the bridge expects. I checked rather
than assumed — `ros2 param list /controller_server` on Jazzy has no
`enable_stamped_cmd_vel`. On Kilted and later, `TwistStamped` is the default
and that bridge line needs changing. `ros_gz_bridge` on Jazzy already has the
`TwistStamped` <-> `gz.msgs.Twist` conversion, so it is a one-line change when
the time comes.

---

## Changes that are not strictly required

Two things I changed that Jazzy would have tolerated as they were.

**`ParameterValue(..., value_type=str)` around the `xacro` `Command`** in the
description launch files. I assumed this was required and then tested it: the
unwrapped form runs fine on Jazzy. I kept the wrapper because it states the
intended type instead of leaving it to inference, but it is not a bug fix and
I am not claiming it as one.

**An `rviz` argument on `testbed_full_bringup.launch.py`**, defaulting to
true. `testbed_navigation` brings up its own map-framed RViz with the nav2
displays, so running both gives two windows. `rviz:=false` on the bringup
avoids that.

# ERIC Robotics Testbed — Reliability Fixes and Validation

## Evidence-based root cause: the room was moved relative to its map

In the supplied workspace, `testbed_gazebo/worlds/testbed_playground.world`
contained this model pose:

```xml
<model name='test_room'>
  <pose>-0.077849 -1.23126 0 0 -0 0</pose>
```

The walls contained in `test_room` were therefore translated by about 7.8 cm
in X and **1.231 m in Y** relative to their original model geometry.

A comparison of the room's actual box collision geometry with the occupied
pixels in `testbed_bringup/maps/testbed_world.pgm` (resolution 0.05 m/pixel)
showed that the best alignment required a displacement of roughly 25 pixels in
Y. Resetting only the `test_room` model's pose to `0 0 0 0 0 0` brings the
walls back to the occupancy map's intended location. The world also contains
independently positioned obstacles; shifting the **whole map** would have
misregistered those objects. The map YAML origin is intentionally unchanged.

**Changed**: `testbed_gazebo/worlds/testbed_playground.world`.

This is a real source-level geometry mismatch. It is a strong explanation for
AMCL's inconsistent corrections and observed 13–16 cm pose discrepancies, but
it is not proof that localization is now accurate; a new Gazebo run is needed.

## Other corrections

- Removed the unused ROS 1 `libgazebo_ros_control.so` plugin reference. The
  independent `libgazebo_ros_diff_drive.so` plugin already provides motion.
- Preserved the previously corrected malformed IMU plugin XML.
- Changed the controller's progress checker to
  `nav2_controller::PoseProgressChecker` (`required_movement_radius=0.10 m`,
  `required_movement_angle=0.15 rad`, `movement_time_allowance=15 s`).
  This allows angular movement during a 180-degree final turn to count as
  progress. It does not mask actual failure to move or localize.
- Kept strict goal completion: `stateful: False`, XY tolerance 0.05 m,
  yaw tolerance 0.10 rad. The RPP path follower is retained.
- Standardized the behavior server's base frame to `base_footprint`.
- Declared runtime RPP and geometry message dependencies and added an
  independent ground-truth goal-checking utility.
- Added a multi-round-trip regression script which fails when either the
  action result or the goal accuracy check fails.

## Local installation / preserving your submitted work

Apply the supplied project files on your `fix/navigation-reliability` branch;
do not replace or reset Git history. The corrected archive is a **source
package**, not a built ROS workspace. It excludes `build`, `install`, `log` and
`.git` from the submitted workspace.

### One complete restart is essential

**Stop all existing** Gazebo, map, localization and Nav2 launch processes
using Ctrl+C. A world-file change will not affect an already-running Gazebo
simulation. Do not start duplicate launch processes.

Build from `~/assignment_ws`:

```bash
source /opt/ros/humble/setup.bash
unset ROS_DISCOVERY_SERVER ROS_SUPER_CLIENT
colcon build --packages-select testbed_description testbed_gazebo testbed_bringup testbed_navigation --symlink-install
source ~/assignment_ws/install/setup.bash
python3 -m unittest discover -s src/level01_ros_assignment/tests -v
```

Open separate terminals, source **both** setups and unset the discovery
server variables in each, then launch **in this order**:

```bash
# Terminal 1: simulation + robot + RViz
ros2 launch testbed_bringup testbed_full_bringup.launch.py
# Terminal 2: map
ros2 launch testbed_navigation map_loader.launch.py
# Terminal 3: localization
ros2 launch testbed_navigation localization.launch.py
# Terminal 4: planner + controller + BT + behaviors
ros2 launch testbed_navigation navigation.launch.py
```

Wait for lifecycle states (`active [3]`) and `gz model -m testbed -p` to
confirm spawn. Gazebo is expected to start near `(0,5,0)`.

### Validate individually

```bash
ros2 run testbed_navigation manual_navigation_test.py 1.0 5.0 --yaw 0.0
ros2 run testbed_navigation report_pose_accuracy.py 1.0 5.0 --yaw 0.0
ros2 run testbed_navigation manual_navigation_test.py 0.0 5.0 --yaw 0.0
ros2 run testbed_navigation report_pose_accuracy.py 0.0 5.0 --yaw 0.0
```

Then run three complete round trips with automatic pass/fail and logging:

```bash
ros2 run testbed_navigation run_navigation_regression.sh 3
```

`report_pose_accuracy.py` checks **AMCL XY <= 0.05 m** and **yaw <= 0.10 rad**,
and separately requires **Gazebo-world XY <= 0.10 m** (configurable) and
**yaw <= 0.10 rad**. To impose 5 cm ground-truth accuracy as well, pass
`--physical-xy-tolerance 0.05` when running the pose reporter alone.
The map and world should now be aligned for this comparison.

### For remaining navigation failures

```bash
ros2 param get /controller_server progress_checker.plugin
ros2 param get /controller_server general_goal_checker.stateful
ros2 topic echo /rosout > /tmp/nav2_errors.log
ros2 topic echo /cmd_vel > /tmp/nav2_commands.log
```

Run the failing navigation action and inspect the Nav2 launch console. Record
Gazebo pose and `/amcl_pose` alongside action feedback. Capture a screenshot
with map, scan, and robot in the same RViz fixed frame (`map`).

## Verification scope

Completed without a ROS runtime: XML/YAML parsing, Python compilation, shell
syntax checks, geometric map-vs-room alignment calculations and static tests.

**Not possible here**: launching Gazebo / AMCL / Nav2, checking the plugin
loads on your particular Ubuntu installation, or measuring navigation success
rates after the world correction. Do not mark runtime issues "resolved" until
the three-round-trip test passes. The initial LiDAR 8 m range is experimental.

## Submission hygiene

`testbed_navigation/package.xml` still contains an auto-generated placeholder
maintainer email and license. Supply the actual maintainer details and the
correct license before final redistribution; they cannot safely be invented.
The new `.gitignore` prevents ROS build artifacts and Python bytecode from
being committed.

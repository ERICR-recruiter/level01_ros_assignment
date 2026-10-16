# ERIC Robotics Level 1 — Development Log

**Date:** 14 October 2026
**Workspace:** `~/assignment_ws`
**ROS distribution:** Humble

## Phase 1 — Workspace and build

- Established `~/assignment_ws` as the workspace root.
- Corrected the missing parentheses in `testbed_description/CMakeLists.txt`.
- Successfully built the description, Gazebo, and bringup packages.
- Added Git ignore rules for generated ROS build artifacts.

## Phase 2 — Robot simulation and sensors

- Corrected the robot-state publisher's simulation-time configuration.
- Removed an incompatible ROS 1 Gazebo control-plugin reference.
- Corrected malformed IMU sensor XML.
- Configured the ROS 2 Gazebo LiDAR plugin, `/scan` remapping, and `lidar_link_1` frame.

## Phase 3 — Validation

- Confirmed successful robot spawning.
- Verified `/odom`, `/clock`, `/scan`, and the LiDAR TF transform.
- Observed approximately 19–24 Hz LiDAR publishing during recent tests.
- Confirmed that a manual `/cmd_vel` test moved the robot. This was a velocity-control test, not autonomous navigation.

## Phase 4 — Initial backlog (completed in later phases)

- Continue investigating the intermittent Gazebo segmentation fault; its root cause remains unresolved.
- Continue investigating timestamp-related TF/message-filter warnings; their root cause remains unconfirmed.
- Initial backlog: implement separate map-loading, localization, and navigation launch files using Nav2 components directly. Completed and validated in later phases.
- Validate the navigation stack and document each implementation stage.

## Development protocol

Use incremental builds during normal development. Use guarded clean rebuilds when justified, and diagnostic builds when investigating failures. Preserve useful logs and crash traces before removing generated artifacts.

Do not label an issue as fixed until its correction has been tested and the result recorded.

## Phase 5 — Map configuration

- Found that `testbed_world.yaml` referenced `wrong_path_testbed_world.pgm`, while the available image is `testbed_world.pgm`.
- Corrected the YAML image path to `testbed_world.pgm`. Verified map-server activation and map visibility in RViz.

## Phase 6 — Manual Nav2 package skeleton

- Created `testbed_navigation` as a sibling package.
- Added map, localization, and navigation launch files without launching `nav2_bringup`.
- Installed package launch/config directories and declared Nav2 runtime dependencies; the canonical map is installed by `testbed_bringup`.
- Verified map-server activation and `/map` publication.
- Python syntax and colcon build checks passed for all three launch files.
- Localization and navigation were subsequently validated in a fresh startup. AMCL became active, `/amcl_pose` was published, `map -> odom` resolved, and a navigation goal succeeded.

## Phase 7 — Autonomous navigation test

- Verified all five navigation lifecycle nodes were active.
- Verified `/navigate_to_pose` was provided by `bt_navigator`.
- Sent a short goal from approximately (-0.03, 4.95) to (0.09, 4.47).
- Controller reported `Reached the goal!`; behavior-tree navigator reported `Goal succeeded`.
- Observed displacement was approximately 0.495 m.
- Nonfatal warnings: the controller defaulted to `general_goal_checker`, and the behavior-tree tick target was exceeded under the current simulation load.


## Phase 8 — Repeatability and LiDAR validation

- Repeated the manual startup workflow successfully after restarting the terminals.
- Increased the LiDAR maximum range from 1.5 m to 10.0 m.
- Verified a scan with 220 finite returns out of 300 rays; 80 rays returned positive infinity.
- Saved `testbed_description/rviz/full_bringup.rviz` with Fixed Frame `map` and the enabled `/map` display using Reliable/Transient Local QoS.
- Reinitialized AMCL after simulation startup and confirmed a pose estimate near the expected spawn position.
- Observed successful navigation with reduced pose flickering after the sensor-range change.
- Gazebo's intermittent segmentation fault and timestamp-related warnings remain unresolved.

## Phase 9 — Cross-machine validation (2026-10-16)

- Tested commit `f1f18dc` on a college PC running Ubuntu 22.04.5,
  ROS 2 Humble and Gazebo Classic 11.10.2.
- `rosdep` reported all dependencies installed; all four workspace
  packages built successfully.
- Without the GDB wrapper, Gazebo remained alive for more than 30 seconds.
  Localization accepted the initial pose near `(0, 5)`, and a 2D Goal
  Pose completed successfully.
- The laptop has also had a stable GDB-wrapped session after earlier
  `gzserver` exit-code `-11` crashes. The cause of those crashes remains
  unconfirmed; success on the college PC does not isolate the cause.


## Phase 10 — Final laptop navigation validation (2026-10-16)

- Rebuilt all four workspace packages successfully and checked the
  individual launch files and combined launch arguments.
- Launched the simulation with the persistent GDB wrapper.
- Started localization using the canonical map in `testbed_bringup`
  and the dedicated `testbed_navigation/config/amcl_params.yaml`.
- Initialized the approximate robot pose near `(0, 5)`.
- Sent a 2D Goal Pose. The controller logged `Reached the goal!`
  and the BT navigator logged `Goal succeeded`.
- A later LiDAR message-filter warning reported an older timestamp
  than the TF transform cache. Navigation succeeded, but this warning
  and the earlier intermittent Gazebo crash remain unresolved.

# Testbed Navigation — ROS 2 Humble

## Overview
A modular Nav2 workflow for the Testbed robot. The package launches
Nav2 components directly instead of calling nav2_bringup.

## Package contents
- launch/map_loader.launch.py: standalone map loading.
- launch/localization.launch.py: map server, AMCL and lifecycle manager.
- launch/navigation.launch.py: planner, controller, smoother,
  behavior server, BT navigator and lifecycle manager.
- launch/full_navigation.launch.py: convenience orchestration launch.
- config/amcl_params.yaml: AMCL localization parameters.
- config/nav2_params.yaml: map-server and navigation parameters.
- The canonical occupancy map lives in `testbed_bringup/maps/`.

## Tested startup sequence

Every terminal should source ROS and the workspace:
`source /opt/ros/humble/setup.bash`
`source ~/assignment_ws/install/setup.bash`

Terminal 1 — Simulation and RViz:
`ros2 launch testbed_bringup testbed_full_bringup.launch.py gui:=false`

Terminal 2 — Localization:
`ros2 launch testbed_navigation localization.launch.py`

Wait until map_server and AMCL are active. The localization launch
already includes map_server; do not launch map_loader alongside it.

Terminal 4 — Initialize the robot near its spawn position (0, 5):
Publish a geometry_msgs/msg/PoseWithCovarianceStamped message on
/initialpose with header.frame_id set to map, position x=0, y=5,
and orientation quaternion (0, 0, 0, 1).

Confirm /amcl_pose publishes and map -> odom resolves.

Terminal 3 — Navigation:
`ros2 launch testbed_navigation navigation.launch.py`

Wait for navigation nodes to become active, then send a reachable
Nav2 Goal from RViz.

## RViz configuration
Configuration: testbed_description/rviz/full_bringup.rviz
Fixed Frame: map
Map topic: /map
Reliability: Reliable
Durability: Transient Local

If the map display says No map received, confirm map_server is active
and toggle the Map display off and on.

## Known limitations
- Initial pose must be provided after a fresh simulation startup.
- LiDAR maximum range was increased from 1.5 m to 10 m. One test
  produced 220 finite returns out of 300 rays.
- Gazebo has intermittently exited with segmentation fault -11;
  the root cause remains unconfirmed.
- Timestamp-related TF/message-filter warnings have occurred;
  their root cause remains unconfirmed.

## Build
From ~/assignment_ws, source ROS Humble and run
`colcon build --symlink-install`.

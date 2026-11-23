# testbed_navigation

Manual Nav2 workflow for Testbed-T1.0.0 (ROS2 Humble, Gazebo Classic 11).
`nav2_bringup` is not used: map server, AMCL, planner, controller, behaviors and
the BT navigator are each launched from their own file with their own parameters.

## Structure
```
testbed_navigation/
├── config/
│   ├── map_server_params.yaml   # map_server
│   ├── amcl_params.yaml         # AMCL (likelihood field, differential model)
│   └── nav2_params.yaml         # controller, planner, behaviors, BT navigator, costmaps
└── launch/
    ├── map_loader.launch.py     # map_server + lifecycle manager
    ├── localization.launch.py   # map_loader + AMCL + lifecycle manager
    └── navigation.launch.py     # controller, planner, behavior, bt_navigator + lifecycle manager
```

## Build
    cd ~/assignment_ws && colcon build --symlink-install && source install/setup.bash

## Run (one terminal each, each sourced)
1. Simulation (Gazebo + RViz):
       ros2 launch testbed_bringup testbed_full_bringup.launch.py
2. Map + localization (`localization.launch.py` already starts the map server):
       ros2 launch testbed_navigation localization.launch.py
3. Set the initial pose at the spawn point (0, 5) facing +x. Publishing it directly is
   the most reliable way (RViz sends clicks in its Fixed Frame, which must already be `map`):
       ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
       "{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 5.0}, orientation: {w: 1.0}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.0685]}}"
   Then set RViz Fixed Frame to `map`. The scan should sit on the map walls.
4. Navigation:
       ros2 launch testbed_navigation navigation.launch.py
5. Send a goal with RViz "Nav2 Goal", or:
       ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
       "{pose: {header: {frame_id: map}, pose: {position: {x: 1.5, y: 5.0}, orientation: {w: 1.0}}}}" --feedback

`map_loader.launch.py` can also be run on its own just to view the map.

## Design choices (basic navigation only)
| Component | Choice | Reason |
|---|---|---|
| Map | `nav2_map_server` | provided `testbed_world.yaml` |
| Localization | AMCL, likelihood-field laser model, differential motion model | 2D lidar + diff-drive base |
| Global planner | NavfnPlanner | simple and reliable |
| Local planner | DWB | basic, no extra tuning needed |
| Behavior tree | default Nav2 trees | spin / backup / wait recoveries via `behavior_server` |
| Costmaps | static + obstacle + inflation (global); obstacle + inflation (local) | lidar on `/scan` |
| Lifecycle | one lifecycle manager per stage | stages start independently |

Frames and topics (from the robot description): `map -> odom -> base_footprint -> base_link`,
`/scan`, `/odom`, `/cmd_vel`. Robot radius 0.25 m (estimated from URDF extents).

## Challenges
- **Starter-code bugs** broke the pipeline before navigation could start (wrong map image path,
  map and world misaligned by ~1.2 m, `maps/` and `models/` not installed, a CMake `ament_package`
  without parentheses, a ROS1 plugin, a 1.5 m lidar range, and others). All are listed in
  `../BUGS.txt`.
- **`map` frame did not exist** until AMCL received an initial pose, so the global costmap warned
  about a missing transform. Fix: start localization first and publish `/initialpose` in the `map` frame.
- **BT navigator failed to activate** because `plugin_lib_names` lacked
  `nav2_compute_path_through_poses_action_bt_node`, which the default Humble trees use.
  The full Humble plugin list is now in `nav2_params.yaml`.
- **Gazebo Classic hanging on "Preparing your world"** under WSL2 from leftover `gzserver`
  processes. Fix: kill stale processes before each run and disable the online model database.

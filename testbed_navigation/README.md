# testbed_navigation

A manual Nav2 setup for the Testbed-T1.0.0 robot. Instead of calling
`nav2_bringup`, each part of the stack is started by its own launch file, using
the individual Nav2 nodes directly.

## Package layout

```
testbed_navigation/
├── config/
│   ├── amcl_params.yaml     # AMCL localization parameters
│   └── nav2_params.yaml     # planner, controller, costmaps, BT navigator, behaviors
├── launch/
│   ├── map_loader.launch.py     # map_server + lifecycle manager
│   ├── localization.launch.py   # map_server + amcl + lifecycle manager
│   └── navigation.launch.py     # controller, planner, behaviors, bt_navigator + lifecycle manager
└── rviz/
    └── navigations.rviz         # RViz layout used for testing
```

## What each launch file does

| Launch file | Nodes | Purpose |
|---|---|---|
| `map_loader.launch.py` | `map_server`, `lifecycle_manager` | Loads `testbed_bringup/maps/testbed_world.yaml` and publishes `/map`. |
| `localization.launch.py` | `map_server`, `amcl`, `lifecycle_manager_localization` | Publishes the map and the `map -> odom` transform. |
| `navigation.launch.py` | `controller_server`, `planner_server`, `behavior_server`, `bt_navigator`, `lifecycle_manager_navigation` | Plans and follows paths to a goal. Expects localization to be running. |

All Nav2 servers are lifecycle nodes. The lifecycle managers configure and
activate them (`autostart: True`), and `node_names` lists them in order. The map
server comes before AMCL because AMCL needs `/map` when it configures.

## How to run

Start each step in its own terminal and leave it running. The nodes use
`use_sim_time: true`, so Gazebo (which publishes `/clock`) must be running first.

```bash
colcon build --symlink-install
source install/setup.bash

# 1. Simulation: Gazebo + robot + RViz
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# 2. Map + localization
ros2 launch testbed_navigation localization.launch.py

# 3. Navigation
ros2 launch testbed_navigation navigation.launch.py
```

(With pixi, prefix each command with
`pixi run bash -c "source install/setup.bash && ..."`.)

In RViz: set the Fixed Frame to `map`, add the Map display on `/map` with
Durability Policy = Transient Local, a PoseArray on `/particle_cloud` and a
LaserScan on `/scan`. Then use **2D Goal Pose** to send a goal. A goal can also be
sent from the command line:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.0, y: 3.0}, orientation: {w: 1.0}}}}"
```

To test the map on its own, run `map_loader.launch.py` (do not run it together with
`localization.launch.py`; both start a node named `map_server`).

## Approach and key parameter choices

- **Map loading.** `map_server` reads the provided yaml. The yaml path comes from
  `get_package_share_directory('testbed_bringup')`, so the map folder must be
  installed by `testbed_bringup` (it was not in the starter code, see
  `bugs_report.txt`).
- **Localization.** AMCL with the differential motion model
  (`nav2_amcl::DifferentialMotionModel`) and the likelihood-field laser model.
  Frames are `map`, `odom`, `base_footprint`. The initial pose is x = 0, y = 5,
  the same point where `spawn_testbed.launch.py` places the robot (checked to be
  free space on the map). `laser_max_range` is 6.0 to match the simulated lidar.
- **Global planner.** `nav2_navfn_planner/NavfnPlanner` on the global costmap
  (static layer + obstacle layer + inflation layer).
- **Local planner.** DWB (`dwb_core::DWBLocalPlanner`) on a 3 x 3 m rolling local
  costmap in the `odom` frame, with a speed limit of 0.26 m/s and 1.0 rad/s.
- **Behavior tree.** Nav2's default `navigate_to_pose_w_replanning_and_recovery`
  tree, with the full BT plugin list loaded. Recoveries (spin, backup, wait) come
  from `behavior_server`.
- **Footprint.** The chassis is about 0.35 x 0.35 m and is not centred on
  `base_footprint`, so the costmaps use a footprint polygon around
  `base_footprint` instead of a circle.
- **Lidar range.** The lidar in the starter robot description sees only 1.5 m,
  which is too short for AMCL to localize reliably in this map (the pose drifted
  away from the Gazebo ground truth). The range was raised to 6.0 m in
  `testbed.gazebo`, and the Nav2 values match it: `laser_max_range: 6.0`,
  `raytrace_max_range: 6.0` and `obstacle_max_range: 5.5`.
- **Not used.** `velocity_smoother` and `collision_monitor` were left out because
  only basic navigation is required.

## Challenges

- **Bugs in the starter code.** Wrong map path, missing install rules, a missing
  `()` after `ament_package`, an unavailable plugin, and wheel and friction values
  that did not match the robot. All are listed in `bugs_report.txt` at the repo
  root.
- **Odometry stability.** The diff-drive plugin used a wheel separation of 0.35 m
  while the wheels are about 0.376 m apart, and the fixed casters had the same
  friction as the wheels. Correcting these reduced drift.
- **Clock and lifecycle.** With `use_sim_time: true` the nodes do nothing until
  Gazebo publishes `/clock`, so the simulation has to be started first. RViz must
  also run with sim time (the provided bringup launch does this).
- **macOS setup.** Development was done on macOS (Apple silicon) with ROS 2 Humble
  from RoboStack (pixi). An older package pin made `gzserver` crash with the
  `libgazebo_ros_factory` plugin. Removing the `setuptools` pin in `pixi.toml`
  resolved newer packages and fixed it. The launch files and parameters
  themselves contain nothing macOS specific and use only standard Nav2 packages.

## Use of AI assistance

An AI assistant (Claude) was used while working on this assignment for
explaining Nav2 concepts, drafting the parameter and launch files, and debugging.
The setup was run, tested and adjusted on the simulation.

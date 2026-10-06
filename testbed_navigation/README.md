# testbed_navigation

Manual Nav2 setup for the Testbed-T1.0.0 robot. It does not use `nav2_bringup`;
each part of the stack has its own launch file and starts the Nav2 nodes directly.

## Package layout

```
testbed_navigation/
├── config/
│   ├── amcl_params.yaml     # AMCL parameters
│   └── nav2_params.yaml     # planner, controller, costmaps, BT navigator, behaviors
├── launch/
│   ├── map_loader.launch.py     # map_server
│   ├── localization.launch.py   # map_server + amcl
│   └── navigation.launch.py     # controller, planner, behaviors, bt_navigator
└── rviz/
    └── navigations.rviz         # RViz layout for testing
```

| Launch file | Nodes | What it does |
|---|---|---|
| `map_loader.launch.py` | `map_server` | Loads `testbed_bringup/maps/testbed_world.yaml` and publishes `/map`. |
| `localization.launch.py` | `map_server`, `amcl` | Publishes the map and the `map -> odom` transform. |
| `navigation.launch.py` | `controller_server`, `planner_server`, `behavior_server`, `bt_navigator` | Plans and follows a path to a goal. Needs localization running. |

Each launch file also starts a `lifecycle_manager`, because Nav2 nodes are
lifecycle nodes and must be configured and activated.

## How to run

Build the workspace, then start each step in its own terminal and keep it running.
Gazebo must be running first because the nodes use `use_sim_time: true`.

```bash
colcon build --symlink-install
source install/setup.bash
```

```bash
# 1. Simulation (Gazebo + robot + RViz)
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

```bash
# 2. Map + localization
ros2 launch testbed_navigation localization.launch.py
```

```bash
# 3. Navigation
ros2 launch testbed_navigation navigation.launch.py
```

In RViz set the Fixed Frame to `map`, then use **2D Pose Estimate** if the particle
cloud does not match the robot, and **2D Goal Pose** to send a goal. A goal can also
be sent from the terminal:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.0, y: 3.0}, orientation: {w: 1.0}}}}"
```

To test only the map, run `map_loader.launch.py` instead of `localization.launch.py`
(both start a node called `map_server`, so do not run them together).

## Main choices

- **Map:** `map_server` loads the provided yaml through the `testbed_bringup` package.
- **Localization:** AMCL, differential motion model, likelihood-field laser model.
  Frames are `map`, `odom` and `base_footprint`. The initial pose is x = 0, y = 5,
  where the robot is spawned.
- **Global planner:** `NavfnPlanner` on a global costmap (static + obstacle + inflation).
- **Local planner:** DWB on a 3 x 3 m rolling local costmap in the `odom` frame.
- **Behavior tree:** Nav2's default navigate-to-pose tree, with spin, backup and wait
  recoveries from `behavior_server`.
- **Footprint:** a polygon around `base_footprint`, because the chassis is not centred
  on that frame.
- **Lidar range:** raised from 1.5 m to 6.0 m in the robot description (AMCL could not
  localize reliably with 1.5 m). The AMCL and costmap ranges match it.
- `velocity_smoother` and `collision_monitor` are not used; only basic navigation
  is needed.

## Bugs and challenges

Bugs found in the starter code and their fixes (map path, install rules,
`ament_package()`, plugin, wheel separation, friction, lidar range) are listed in
`bugs_report.txt` in the repository root.

Other things that needed care:

- The nodes do nothing until Gazebo publishes `/clock`, so start the simulation first.
- The diff-drive wheel separation did not match the robot, which caused odometry drift.
- With a 1.5 m lidar AMCL drifted away from the true pose, and the global plan then
  fell outside the local costmap.

## Development environment

This was developed on **macOS (Apple silicon)**, not Ubuntu 22.04, using **pixi**
with ROS 2 Humble from the RoboStack channel. Pixi provided ROS 2 Humble, Gazebo
Classic 11 and Nav2. On macOS the commands above were run through pixi (for example
`pixi run ros2 launch ...`). The launch files and parameters use only
standard Nav2 packages and do not depend on pixi, so they work the same on a normal
ROS 2 Humble install.

## AI assistance

An AI assistant (Claude) helped with explaining Nav2, drafting the parameter and
launch files, and debugging. All files were run and tested in the simulation.

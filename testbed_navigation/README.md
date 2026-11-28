# testbed_navigation

Manual Nav2 navigation workflow for **Testbed-T1.0.0**. Each stage is its own launch
file and its own parameter file, so map loading, localization and navigation can be
started and debugged independently. `nav2_bringup` is not used.

## Package layout

```
testbed_navigation/
├── config/
│   ├── map_server_params.yaml   # nav2_map_server
│   ├── amcl_params.yaml         # nav2_amcl
│   └── nav2_params.yaml         # planner, controller, costmaps, BT, behaviours, smoother
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
└── rviz/navigation.rviz         # map + scan + robot + TF, fixed frame "map"
```

## Run order

Build from the workspace root:

```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
```

Terminal 1 — simulation (Gazebo + robot_state_publisher + spawn + RViz):

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

Terminal 2 — load the map:

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

Terminal 3 — localize:

```bash
ros2 launch testbed_navigation localization.launch.py
```

In RViz use **2D Pose Estimate** on the robot's actual start pose
(`x=0, y=5` in the supplied world) so AMCL has a sensible prior. The pose can also
be sent from the shell:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "header: {frame_id: map}
pose: {pose: {position: {x: 0.0, y: 5.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}"
```

Terminal 4 — start the navigation stack:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Send a goal with RViz's **2D Goal Pose**, or:

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "header: {frame_id: map}
pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"
```

Optional RViz config:

```bash
rviz2 -d $(ros2 pkg prefix testbed_navigation)/share/testbed_navigation/rviz/navigation.rviz
```

## What each launch file does

| Launch file | Nodes | Lifecycle group |
|-------------|-------|-----------------|
| `map_loader.launch.py` | `nav2_map_server/map_server` | `map_server` |
| `localization.launch.py` | `nav2_amcl/amcl` | `amcl` |
| `navigation.launch.py` | `controller_server`, `smoother_server`, `planner_server`, `behavior_server`, `bt_navigator`, `waypoint_follower`, `velocity_smoother` | all seven, with `autostart` |

`map_loader` passes the map YAML as the `yaml_filename` parameter override. AMCL gets
its own YAML so it can be tuned without touching the navigation stack. The navigation
file wires `cmd_vel` through the velocity smoother (`cmd_vel_nav` → `cmd_vel`) and
sets the BT XML explicitly. All nodes use the Gazebo clock.

Plugin choices (basic navigation only):

- Global planner: `nav2_navfn_planner/NavfnPlanner`
- Local controller: `dwb_core::DWBLocalPlanner`
- Costmaps: `StaticLayer` + `ObstacleLayer` + `InflationLayer` (global),
  `VoxelLayer` + `InflationLayer` (local)
- BT: `navigate_to_pose_w_replanning_and_recovery.xml`
- Recovery behaviours: spin, backup, drive on heading, wait, assisted teleop
- Smoother: `nav2_smoother::SimpleSmoother`

The LiDAR in the supplied URDF has a 1.5 m maximum range, so the costmap raytrace and
obstacle ranges are clamped to 1.4 m instead of Nav2's 2.5–3.0 m defaults.

## Verification

- `colcon build --symlink-install` succeeds for all four packages.
- All three launch files are accepted by `ros2 launch --show-args`.
- With the simulation running, `/map`, `/map_metadata`, `/amcl_pose` and
  `/navigate_to_pose` appear and all lifecycle nodes reach `active`.
- A goal sent to `/goal_pose` moves the robot without colliding with the test room.

## Screenshots

Captured from RViz with `rviz/navigation.rviz` during the verification run:

- `../screenshots/01_localization.png` — loaded map, laser scan and AMCL pose after the initial pose.
- `../screenshots/02_navigation.png` — robot navigating towards a goal.
- `../screenshots/03_fitted_window.png` — fitted RViz window with the loaded map, scan and localized robot.
- `../screenshots/04_fitted_navigation.png` — fitted RViz window after a navigation goal.

## Challenges

- The starter map YAML pointed at a nonexistent PGM and the map directory was not
  installed by CMake; both are fixed and listed in `BUGS_FOUND.txt` at the repo root.
- Gazebo odom is published on `odom` → `base_footprint`, while Nav2's costmaps and BT
  use `base_link`; the static TF from `robot_state_publisher` bridges them, so both
  frame names are kept as provided.
- AMCL starts unlocalized; a 2D Pose Estimate is required before goals are reliable.

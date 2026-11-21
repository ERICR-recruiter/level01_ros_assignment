# testbed_navigation

Nav2 navigation for the **Testbed-T1.0.0** robot (ROS 2 Humble, Gazebo Classic 11). Each Nav2 component is started from its own launch file without `nav2_bringup`. See the [root README](../README.md) for the overview and [`BUGS.md`](../BUGS.md) for the starter-bug fixes.

**Demo video:** [Watch on YouTube](https://youtu.be/d_YL__skTAc)

## Package structure

```
testbed_navigation/
├── config/
│   ├── map_server_params.yaml    # map server topic and frame
│   ├── amcl_params.yaml          # AMCL localization
│   └── nav2_params.yaml          # planner, controller, costmaps, behaviors, BT navigator,
│                                 #   waypoint follower, velocity smoother, collision monitor
├── launch/
│   ├── map_loader.launch.py      # map_server
│   ├── localization.launch.py    # map loader + AMCL
│   ├── navigation.launch.py      # Nav2 servers
│   └── bringup_all.launch.py     # robot, Gazebo, localization, navigation, RViz
├── rviz/navigation.rviz          # saved RViz layout
├── scripts/patrol.py             # 3-waypoint patrol (nav2_simple_commander)
└── docs/images/                  # screenshots used in this README
```

## Launch files

| Launch file | Starts |
|---|---|
| `map_loader` | `map_server` and its lifecycle manager |
| `localization` | map loader, `amcl` and its lifecycle manager |
| `navigation` | `controller_server`, `planner_server`, `behavior_server`, `bt_navigator`, `waypoint_follower`, `velocity_smoother`, `collision_monitor` and a lifecycle manager |
| `bringup_all` | robot description, Gazebo, spawn, localization (after 10 s), navigation (after 17 s), RViz (after 20 s) |

Arguments: `use_sim_time` (default true), `map`, `map_params_file`, `amcl_params_file`, `nav2_params_file`, `rviz_config`. All nodes start through lifecycle managers with `autostart`.

## Run

```bash
ros2 launch testbed_navigation bringup_all.launch.py
```

Wait about 20 s, then set goals with **2D Goal Pose** in RViz. The initial pose comes from `amcl_params.yaml`. To run parts separately on top of a running simulation (`ros2 launch testbed_bringup testbed_full_bringup.launch.py`):

```bash
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
ros2 launch testbed_navigation navigation.launch.py
```

Patrol demo (three waypoints, then back to the start):

```bash
ros2 run testbed_navigation patrol.py --ros-args -p use_sim_time:=true
```

## Command path

```
controller_server / behavior_server ─► /cmd_vel_nav ─► velocity_smoother
 ─► /cmd_vel_smoothed ─► collision_monitor ─► /cmd_vel ─► robot
```

## Key parameters

| Component | Setting |
|---|---|
| Map | 405 × 400 cells, 0.05 m, origin (-10.2, -9.94) |
| AMCL | likelihood field, differential motion model, 500-2000 particles, initial pose (0, 5, yaw 0) |
| Global planner | `NavfnPlanner`, tolerance 0.5 m, unknown space allowed |
| Local controller | `DWBLocalPlanner`, 20 Hz, max 0.26 m/s and 1.0 rad/s |
| Goal tolerance | 0.25 m position, 0.25 rad yaw |
| Costmaps | global: static + obstacle + inflation; local: 3 m rolling window; robot radius 0.3 m, inflation 0.55 m |
| Behaviors | `spin`, `backup`, `drive_on_heading`, `wait` |
| Velocity smoother | accel limits 1.0 m/s² and 2.0 rad/s² |
| Collision monitor | stop zone (0.6 m × 0.5 m) around the robot, triggered by at least 4 lidar points |

## Trial results

Five scenarios were tested: same room, doorway, other room, goal on a wall, and obstacle replan. Temporary scripts were written to run the repeated trials and record the numbers; they were used for testing only and are not part of the final repo. Metrics were recorded for the first three goals (5 trials each, same start pose).

| Metric | Goal 1 (same room) | Goal 2 (doorway) | Goal 3 (other room) |
|---|---|---|---|
| Goal X (m) | 6.626 | -6.738 | -4.364 |
| Goal Y (m) | 4.253 | 2.837 | -5.114 |
| Goal Yaw (rad) | -1.560 | -1.598 | -0.017 |
| Successful trials | 5 / 5 | 5 / 5 | 5 / 5 |
| Success rate (%) | 100 | 100 | 100 |
| Avg. navigation time (s) | 28.22 | 33.12 | 68.76 |
| Avg. final error (m) | 0.215 | 0.252 | 0.245 |
| Avg. path length (m) | 6.808 | 7.316 | 16.285 |
| Avg. velocity (m/s) | 0.241 | 0.221 | 0.235 |

Speed stays around 0.22-0.24 m/s, just under the 0.26 m/s limit, so time grows almost linearly with path length. Final error sits near the 0.25 m goal tolerance because the robot stops as soon as it is inside it. The wall-goal and obstacle-replan scenarios also completed successfully.

## Demo and screenshots

**Demo video:** [Watch on YouTube](https://youtu.be/d_YL__skTAc)

**RViz: system view.** Map with inflated costmap, AMCL particle cloud, laser scan and the planned path (`/plan`) to a goal.

![RViz system view](docs/images/rviz_setup.png)

**Gazebo: simulation world.** Top view of the test room the robot navigates.

![Gazebo world](docs/images/gazebo_sim.png)

## Starter bugs

Eight bugs in the starter packages were found and fixed (build error, wrong map path, map not installed, 1.5 m lidar range, IMU XML typo, missing `use_sim_time`, CRLF line endings, missing dependencies). How each was found and fixed is explained in [`BUGS.md`](../BUGS.md) in the repo root.

## Troubleshooting

- **Nothing happens after launch:** give `bringup_all` about 20 s, then check `ros2 action list` for `navigate_to_pose`.
- **Robot not localized:** the initial pose matches the spawn pose (0, 5). If you change the spawn, change it in `amcl_params.yaml` too, or use **2D Pose Estimate**.
- **Timeouts or missing sensor data:** try Cyclone DDS (`export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`).

## Possible further changes

- Tighten `xy_goal_tolerance` (for example 0.10 m) and re-measure final error.
- Raise the velocity limits, since travel time is capped by speed.
- Collect metrics for the wall-goal and replan scenarios.
- Try other planners and controllers (Smac, MPPI, Regulated Pure Pursuit).

## Author

**Vedant Anant Kulkarni**, BVCOE | vedantkulkarni252@gmail.com | GitHub: vedant710 | License: Apache-2.0
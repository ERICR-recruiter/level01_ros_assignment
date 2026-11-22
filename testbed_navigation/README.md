# testbed_navigation

Manual Nav2 bringup for the Testbed-T1.0.0 robot on ROS 2 Humble and Gazebo Classic 11.

This package doesn't use `nav2_bringup`. It starts each Nav2 server itself, in three launch files that build on each other: map loading, then localization, then navigation. Each layer can be launched and tested on its own.

## Demo

- Video: _link to be added_
- Screenshots: _to be added_

## Package layout

```
testbed_navigation/
├── launch/
│   ├── map_loader.launch.py     # map_server + its lifecycle manager
│   ├── localization.launch.py   # includes map_loader, adds AMCL + its lifecycle manager
│   └── navigation.launch.py     # includes localization, adds planner/controller/behaviors/BT navigator
├── config/
│   ├── amcl_params.yaml         # AMCL parameters
│   └── nav2_params.yaml         # costmaps, planner, controller, behaviors, BT navigator
├── maps/
│   ├── testbed_world.yaml       # copy of testbed_bringup/maps/testbed_world.yaml
│   └── testbed_world.pgm
├── CMakeLists.txt
└── package.xml
```

## Requirements

- Ubuntu 22.04, ROS 2 Humble, Gazebo Classic 11 (`gazebo_ros`)
- Nav2 for Humble (`ros-humble-navigation2`)
- `teleop_twist_keyboard` (optional, for testing localization by hand)

## Build

```bash
cd ~/assignment_ws
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install
source install/setup.bash
```

## How to run

Start the simulation first, in its own terminal:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

Then start **one** of the following in a second terminal. Each file includes the layer below it.

| Goal | Command | Nodes started |
|---|---|---|
| Map only | `ros2 launch testbed_navigation map_loader.launch.py` | `map_server`, `lifecycle_manager_map` |
| Map + localization | `ros2 launch testbed_navigation localization.launch.py` | above + `amcl`, `lifecycle_manager_localization` |
| Full navigation | `ros2 launch testbed_navigation navigation.launch.py` | above + `planner_server`, `controller_server`, `behavior_server`, `bt_navigator`, `lifecycle_manager_navigation` |

All three accept the same launch arguments:

| Argument | Default | Meaning |
|---|---|---|
| `map` | `share/testbed_navigation/maps/testbed_world.yaml` | Full path to the map YAML |
| `use_sim_time` | `true` | Use Gazebo's `/clock` |

To navigate, click **2D Goal Pose** in RViz. The robot starts localized at its spawn pose, so **2D Pose Estimate** is only needed to reset localization.

## Architecture

```
Gazebo ──/scan, /odom, odom→base_footprint TF──┐
robot_state_publisher ──base_footprint→sensors TF┤
                                                 ▼
map_server ──/map──► amcl ──map→odom TF──► global_costmap ─► planner_server ─┐
                                                                             ▼
RViz goal ─► bt_navigator (NavigateToPose BT) ─► /compute_path_to_pose ──────┘
                     │                          /follow_path ─► controller_server ─► /cmd_vel ─► Gazebo
                     └─ recovery: spin / backup / wait ─► behavior_server
```

### Lifecycle management

Nav2 servers are lifecycle nodes. They start *unconfigured* and do nothing until they are configured and activated. Each launch file has its own `nav2_lifecycle_manager` with `autostart: true` that manages only the nodes that file starts:

| Lifecycle manager | Manages |
|---|---|
| `lifecycle_manager_map` | `map_server` |
| `lifecycle_manager_localization` | `amcl` |
| `lifecycle_manager_navigation` | `planner_server`, `controller_server`, `behavior_server`, `bt_navigator` |

I used one manager per layer so each layer can be started, stopped and debugged independently, which is the modularity the assignment asks for. The cost is that the layers have no shared start-up order. In practice this is fine, because AMCL waits for the map and the costmaps wait for the `map → odom` transform.

### TF tree

```
map ──(amcl)──► odom ──(gazebo diff_drive)──► base_footprint ──(robot_state_publisher)──► base_link ──► lidar_link_1, imu_link_1, wheels, casters
```

## Configuration

### Map (`map_loader.launch.py`)

`map_server` loads `maps/testbed_world.yaml` (0.05 m/cell, 405 × 400 cells, origin `(-10.2, -9.94)`). The map is published once, with Transient Local durability, so RViz's Map display must also be set to Transient Local to receive it.

The map is a copy of the one in `testbed_bringup/maps/`. I kept a copy so this package runs on its own. A different map can be passed with `map:=/path/to/map.yaml`.

### Localization (`config/amcl_params.yaml`)

| Parameter | Value | Why |
|---|---|---|
| `base_frame_id` / `odom_frame_id` / `global_frame_id` | `base_footprint` / `odom` / `map` | Match the frames published by the diff-drive plugin and the URDF |
| `scan_topic` | `/scan` | Lidar topic from the Gazebo ray sensor |
| `robot_model_type` | `nav2_amcl::DifferentialMotionModel` | Differential-drive robot (Humble plugin name) |
| `laser_min_range` / `laser_max_range` | 0.10 / 10.0 m | Same as the lidar's `<range>` in `testbed.gazebo` |
| `laser_model_type` | `likelihood_field` | Nav2 default; works well with a static occupancy map |
| `min_particles` / `max_particles` | 500 / 2000 | Nav2 defaults; enough for a 20 m × 20 m map |
| `max_beams` | 60 | Of the 300 lidar samples, 60 are used per update |
| `update_min_d` / `update_min_a` | 0.20 m / 0.15 rad | Filter updates after this much motion |
| `alpha1`–`alpha5` | 0.2 | Odometry noise model; Nav2 defaults |
| `set_initial_pose` / `initial_pose` | `true` / `(0.0, 5.0, yaw 0.0)` | Same as the spawn pose in `spawn_testbed.launch.py`, so the robot is localized at start-up |
| `transform_tolerance` | 1.0 s | Margin for the `map → odom` transform under sim time |

### Navigation (`config/nav2_params.yaml`)

The assignment asks for basic navigation, so I kept the server and plugin set to the minimum needed to plan, follow a path and recover:

| Server | Plugin | Why this one |
|---|---|---|
| `planner_server` | `nav2_navfn_planner/NavfnPlanner` (Dijkstra) | Simple and reliable on a 2D occupancy grid; `tolerance: 0.5`, `allow_unknown: true` |
| `controller_server` | `nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController` | Fewer parameters to tune than DWB for a differential-drive robot, and it slows down on its own near obstacles and in sharp turns |
| `controller_server` | `nav2_controller::SimpleProgressChecker`, `nav2_controller::SimpleGoalChecker` | Goal tolerance 0.20 m / 0.25 rad; abort if the robot moves less than 0.10 m in 20 s |
| `behavior_server` | `Spin`, `BackUp`, `Wait` | The recoveries used by the default behavior tree |
| `bt_navigator` | Humble default `navigate_to_pose_w_replanning_and_recovery.xml` | Replans at 1 Hz and runs recoveries on failure; no custom tree needed |

**Costmaps**

| | Global | Local |
|---|---|---|
| Frame | `map` | `odom`, 3 m × 3 m rolling window |
| Layers | static, obstacle, inflation | obstacle, inflation |
| Resolution | 0.05 m | 0.05 m |

- **Footprint:** `[[0.124, 0.165], [0.124, -0.241], [-0.226, -0.241], [-0.226, 0.165]]` in `base_footprint`. I worked it out from the collision mesh bounds of `base_link` and the wheels. `base_link` is not centred on `base_footprint`, so a polygon fits better than a `robot_radius`.
- **Obstacle layer:** `/scan`, `obstacle_max_range: 9.5`, `raytrace_max_range: 10.0`. Both stay within the lidar's 10 m range.
- **Inflation:** `inflation_radius: 0.35`, `cost_scaling_factor: 3.0`.

**Controller tuning**

| Parameter | Value | Note |
|---|---|---|
| `desired_linear_vel` | 0.3 m/s | Started at 0.15 for first tests, then raised to 0.3. At 0.3 the robot followed the path without oscillation, passed the narrowest gap and stopped within tolerance |
| `lookahead_time` / `min_` / `max_lookahead_dist` | 1.5 s / 0.25 m / 0.60 m | Velocity-scaled lookahead: 0.3 × 1.5 = 0.45 m at cruise speed |
| `rotate_to_heading_angular_vel` | 0.6 rad/s | Turns in place towards the path when the heading error exceeds 0.785 rad |
| `use_collision_detection` | `true` | Stops if a collision is predicted within 1.0 s |

## Verification

| Check | Command | Result |
|---|---|---|
| Map server active | `ros2 lifecycle get /map_server` | `active` |
| Map received | RViz Map display (Transient Local) | Map drawn and lined up with the Gazebo world |
| TF tree complete | `ros2 run tf2_tools view_frames` | `map → odom → base_footprint → base_link → sensors` |
| AMCL publishing | `ros2 run tf2_ros tf2_echo map odom` | Transform published |
| Localization converges | RViz ParticleCloud, `ros2 topic echo /amcl_pose` | Cloud shrinks while driving; covariance decreases; scan lines up with the walls |
| Nav2 servers active | `ros2 lifecycle get /planner_server` (and the others) | `active` |
| Action available | `ros2 action list` | `/navigate_to_pose` listed |
| Navigation | 2D Goal Pose in RViz | `/plan` published and the robot reaches the goal |

## Challenges and how I solved them

1. **Starter-code bugs blocked everything else.** The map YAML pointed to a non-existent image, the `maps` folder wasn't installed, `testbed_description` didn't build, and the lidar range was 1.5 m. I fixed the simulation before writing any Nav2 configuration. All fixes are listed in [`../BUGS_FIXED.txt`](../BUGS_FIXED.txt).
2. **Lidar range too short for localization.** At 1.5 m the scan saw almost nothing in a 20 m map, so AMCL had little to match. I raised the sensor range to 10 m and matched AMCL `laser_max_range` and the costmap ranges to it.
3. **Humble vs. newer Nav2 parameter names.** docs.nav2.org documents the newest release. Some parameters I first copied from it (`bt_navigator` `navigators`, `behavior_server` `local_costmap_topic`, `controller_server` `costmap_update_timeout`) don't exist in Humble, and Humble ignores unknown parameters without any warning. I compared every block with `/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml` and checked loaded values with `ros2 param get`.
4. **Behavior server frame.** In Humble, the recoveries check collisions against the local costmap, so `behavior_server` `global_frame` must be `odom`, not `map`.
5. **Map QoS in RViz.** `map_server` publishes the map once, with Transient Local durability. A Map display left on Volatile durability never receives it, because RViz subscribes after the map was sent. I set the Map display to Transient Local and saved it in `full_bringup.rviz`.
6. **Lifecycle nodes.** Nav2 servers stay inactive without a lifecycle manager. I added one lifecycle manager per launch layer, with `autostart: true`.
7. **Sim time.** All nodes, including `robot_state_publisher`, run with `use_sim_time: true` so TF stamps and Nav2 timeouts use Gazebo's clock.

## Possible next steps

- Add `velocity_smoother` and `collision_monitor` between the controller and `/cmd_vel`.
- Send goals and waypoints from a script with the Nav2 Simple Commander API.
- Start RViz from `navigation.launch.py` with a navigation-only config.

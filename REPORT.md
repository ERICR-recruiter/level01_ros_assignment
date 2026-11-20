# Level 1 ROS 2 Navigation Assignment: Work Report

**Robot:** Testbed-T1.0.0 | **Stack:** ROS 2 Humble, Gazebo Classic 11, Nav2, Cyclone DDS
**Test environment:** the `testbed-nav:humble` Docker image (workspace `Dockerfile` / `Makefile`)

---

## 1. Summary

| Task from the assignment README | Status |
|---|---|
| Find and fix the bugs left in the starter code | Done. 12 bugs fixed, 3 more noted ([`BUGS_FIXED.txt`](BUGS_FIXED.txt)) |
| Bug list text file in the repo root, outside the navigation package | Done (`BUGS_FIXED.txt`) |
| New package `testbed_navigation` | Done |
| `launch/map_loader.launch.py` using `map_server` | Done |
| `config/amcl_params.yaml` + `launch/localization.launch.py` | Done |
| `config/nav2_params.yaml` + `launch/navigation.launch.py` (planner, controller, BT, behaviours, velocity smoother) | Done |
| Proper `CMakeLists.txt` / `package.xml` | Done |
| `README.md` describing the approach and the challenges | Done (`testbed_navigation/README.md`) |
| Video or screenshots of localization and navigation | **Still to do.** Needs a GUI session (see section 7) |

The workspace builds cleanly (`colcon build`: 4 packages finished). In a headless Gazebo simulation,
the robot localized itself and reached two navigation goals in different rooms.

---

## 2. Starting point

- `colcon build` **failed**: `testbed_description/CMakeLists.txt` had a CMake parse error.
- The map yaml referred to an image file that does not exist.
- The Docker setup in the workspace root used `sed`/`cp` steps to work around two of these bugs.

I first read `README.md` and `help.md`. Then I went through every launch, URDF/xacro, Gazebo,
CMake and package file. I also checked the STL mesh bounding boxes and the map image to confirm
the robot's geometry and that the spawn point is in free space.

---

## 3. Bugs fixed in the starter code

Full details are in [`BUGS_FIXED.txt`](BUGS_FIXED.txt).

| # | File | Bug | Fix |
|---|---|---|---|
| 1 | `testbed_description/CMakeLists.txt` | `ament_package` without `()`, so the build fails | `ament_package()` |
| 2 | `testbed_bringup/maps/testbed_world.yaml` | `image: wrong_path_testbed_world.pgm` | `image: testbed_world.pgm` |
| 3 | `testbed_bringup/CMakeLists.txt` | `maps/` not installed | added to `install(DIRECTORY)` |
| 4 | `testbed_gazebo/CMakeLists.txt` | `models/` not installed, but added to `GAZEBO_MODEL_PATH` | added to `install(DIRECTORY)` |
| 5 | `*/package.xml` | missing run-time dependencies | added xacro, robot_state_publisher, gazebo_ros, ... |
| 6 | `robot_description.launch.py` | `robot_state_publisher` not on sim time, so TF timestamps don't match | `use_sim_time: True` (+ `ParameterValue` for the URDF) |
| 7 | `testbed.gazebo` | ROS 1 plugin `libgazebo_ros_control.so` | removed |
| 8 | `testbed.gazebo` | lidar max range **1.5 m**, too short for AMCL in ~10 m rooms | 0.12-12 m, 360 samples, full circle |
| 9 | `testbed.gazebo` | stray `>` in the IMU plugin block | removed |
| 10 | `testbed.gazebo` | wheels mu=0.2 (they slip), fixed casters mu=0.2 (they drag) | wheels mu=1.0 (+kp/kd), casters mu=0.0 |
| 11 | `testbed.gazebo` | `wheel_separation` 0.35 m; the meshes give 0.376 m | 0.376 |
| 12 | `testbed.xacro` | `base_footprint` ~6 cm away from the turning centre between the wheels | joint offset `0.0505 0.0378 0`, so the footprint is now symmetric |

Noted but not changed: `.vscode/settings.json` points to another machine's path, and the IMU and
dummy link frames look swapped relative to their meshes (this doesn't matter for 2D navigation).

---

## 4. The `testbed_navigation` package

```
testbed_navigation/
|-- CMakeLists.txt / package.xml
|-- config/
|   |-- map_server_params.yaml
|   |-- amcl_params.yaml
|   `-- nav2_params.yaml
|-- launch/
|   |-- map_loader.launch.py          # map_server + lifecycle_manager_map
|   |-- localization.launch.py        # amcl + lifecycle_manager_localization (includes the map loader by default)
|   |-- navigation.launch.py          # 5 Nav2 servers + lifecycle_manager_navigation
|   `-- testbed_navigation.launch.py  # all of the above + RViz
|-- rviz/testbed_navigation.rviz
|-- scripts/send_goal.py              # NavigateToPose client for the terminal
`-- README.md
```

### Design

- **Modular.** `nav2_bringup` is not used. Each server is a separate node, and each stage has its
  own lifecycle manager, so the map, localization and navigation stages can each be started and
  debugged on their own.
- **Plugins, kept to what basic navigation needs:**

| Server | Plugin |
|---|---|
| map_server | `nav2_map_server` -> `testbed_bringup/maps/testbed_world.yaml` |
| amcl | `DifferentialMotionModel`, `likelihood_field` laser model, initial pose (0, 5, 0) |
| planner_server | `nav2_navfn_planner/NavfnPlanner` (A*) |
| controller_server | `nav2_regulated_pure_pursuit_controller` (0.35 m/s, rotates to the path heading first, collision checking) |
| behavior_server | Spin, BackUp, DriveOnHeading, Wait |
| bt_navigator | default `navigate_to_pose_w_replanning_and_recovery` tree |
| velocity_smoother | controller -> `/cmd_vel_nav` -> smoother -> `/cmd_vel` |

- **Costmaps:** the global costmap uses static + obstacle + inflation layers, and the local costmap
  (3x3 m rolling window) uses obstacle + inflation. The footprint is a 0.36 x 0.42 m rectangle
  measured from the STL meshes.

---

## 5. Problems found during testing (and fixed)

1. **Launch arguments shared between files.** In Humble, `IncludeLaunchDescription` does not
   scope launch configurations. Every file declared `params_file`, so the AMCL file path leaked
   into `navigation.launch.py`. `controller_server` then started with default settings and failed:
   *"No critics defined for FollowPath"*. Fix: each file uses its own argument name
   (`map_params_file`, `amcl_params_file`, `nav2_params_file`).
2. **"Empty Tree" on every goal.** `default_nav_to_pose_bt_xml: ""` loads an *empty* behaviour tree
   in Humble, so every goal aborted. Fix: leave the parameter unset so the default tree is used.

---

## 6. Verification (headless Docker simulation)

The test script started gzserver (no GUI), robot_state_publisher, the spawned robot and
`testbed_navigation.launch.py`, then sent goals with `send_goal.py`.

| Check | Result |
|---|---|
| Build | 4/4 packages built, URDF passes `check_urdf` |
| Map installed | `share/testbed_bringup/maps/testbed_world.{yaml,pgm}` |
| Lidar | `/scan` `range_max = 12.0` |
| Driving | 0.2 m/s for ~5 s gave ~1.4 m of travel (commands are followed, no stalling) |
| Lifecycle | map_server, amcl, controller, planner, behavior, bt_navigator, velocity_smoother all **active** |
| Initial localization | AMCL pose (0.04, 5.01), spawn point (0, 5) |
| Goal 1: (1.0, -4.0), through the doorway into the room below | **reached**, AMCL pose (1.06, -3.87) |
| Goal 2: (-7.0, 7.0), into the top-left room | **reached**, AMCL pose (-6.93, 6.79) |

Both goals ended within the 0.2 m tolerance of the goal checker.

---

## 7. How to run and what is left to do

```bash
cd ~/assignment_ws && colcon build --symlink-install && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 launch testbed_bringup testbed_full_bringup.launch.py          # terminal 1
ros2 launch testbed_navigation testbed_navigation.launch.py         # terminal 2
ros2 run testbed_navigation send_goal.py 1.0 -4.0 0.0               # or use "Nav2 Goal" in RViz
```
With Docker: `make build && make dev`, then `make shell` for the second terminal.

Still to do before submitting:
1. Record a video or take screenshots of localization (particle cloud) and navigation in RViz and Gazebo.
2. Fill in your name and contact details in `README.md` and the maintainer field in `testbed_navigation/package.xml`.
3. Commit to your fork and open the PR to `main` (nothing has been committed yet).
4. Optional: remove the now-unneeded `sed`/`cp` workaround steps from the workspace `Dockerfile`.

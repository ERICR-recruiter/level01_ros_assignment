# testbed_navigation

Map loading, localization and navigation for Testbed-T1.0.0, built from individual Nav2 nodes without calling `nav2_bringup`.

## Environment

| Item | Version |
|---|---|
| Ubuntu | 26.04 |
| ROS 2 | Lyrical |
| Nav2 | 1.5.2 |
| Gazebo Sim | 10.5.0 |

**This submission targets ROS 2 Lyrical and Gazebo Sim, not ROS 2 Humble and Gazebo 11 as stated in the assignment.** Lyrical was the version available on the development machine, so the starter simulation was ported. The code was not tested on Humble and is not expected to run there unchanged.

## Structure

| File | Purpose |
|---|---|
| `launch/map_loader.launch.py` | `map_server` and its lifecycle manager |
| `launch/localization.launch.py` | `amcl` and its lifecycle manager |
| `launch/navigation.launch.py` | Planner, controller, behavior, BT navigator and velocity smoother servers with their lifecycle manager |
| `config/map_server_params.yaml` | Map server parameters |
| `config/amcl_params.yaml` | AMCL parameters |
| `config/nav2_params.yaml` | Navigation and costmap parameters |

The starter code bugs and fixes are listed in [`bugs_and_fixes.txt`](../bugs_and_fixes.txt).

## Build

```bash
cd ~/assignment_ws
source /opt/ros/lyrical/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

## Run

Use one sourced terminal per command, in this order:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
ros2 launch testbed_navigation navigation.launch.py
```

Wait for `Managed nodes are active` after each of the last three. Then use **2D Goal Pose** in RViz, or:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 5.0, y: 5.0}, orientation: {w: 1.0}}}}"
```

| Bringup option | Default | Effect |
|---|---|---|
| `headless:=true` | `false` | Runs Gazebo without its window |
| `rviz_hidpi_fix:=true` | `false` | Turns off Qt HiDPI scaling in RViz |

The three navigation launch files accept `params_file`, `use_sim_time` and `autostart`. The map loader also accepts `map`.

## Approach

1. **Starter code:** built the untouched code, checked the map, meshes and URDF, then fixed the bugs.
2. **Simulation:** compared odometry with the Gazebo pose to check wheel separation and the rotation centre.
3. **Map, localization, navigation:** added and tested one at a time, each with its own lifecycle manager, so each part can be started and debugged alone.

| Part | Choice | Reason |
|---|---|---|
| Localization | AMCL, differential model, likelihood field | Suits a differential-drive robot with a 2D lidar. The initial pose matches the spawn at (0, 5) |
| Global planner | NavFn, `allow_unknown: false` | Simple grid planner, kept out of unmapped space |
| Controller | Regulated Pure Pursuit, 0.3 m/s | Few parameters, follows paths smoothly and rotates to heading |
| Costmaps | Static (global only), obstacle and inflation layers | The map plus live lidar obstacles, with the footprint measured from the meshes |
| Behaviors | Spin, back up, drive on heading, wait | Used by the default recovery behavior tree |
| Behavior tree | `navigate_to_pose_w_replanning_and_recovery.xml` | Replanning and recovery from Nav2 |
| Velocity smoother | 0.5 m/s², 1.5 rad/s² | Limits acceleration before `cmd_vel` |

Velocity path: controller and behaviors → `cmd_vel_nav` → velocity smoother → `cmd_vel` → bridge → Gazebo.

## Results

Measured in simulation against the Gazebo pose.

**Localization**

| Test | Result |
|---|---|
| While driving | 0.03 to 0.09 m, within 1° |
| Initial pose wrong by 0.58 m and 18° | 0.07 m and 0.4° after a half turn |
| Scan against map | All returned rays within about 0.15 m of a mapped wall, in three checks |

**Navigation**

| Goal | Result | Simulated time | Final error |
|---|---|---|---|
| (5, 5), same room | Succeeded | 17.8 s | 0.16 m, 0.4° |
| (3.6, -3), lower-right room | Succeeded | 30.8 s | 0.10 m, 3.4° |
| (-6, 3), left room | Succeeded | 52.1 s | 0.16 m, 1.6° |
| (-3.03, 1.5), inside a wall | Aborted as expected | 14.5 s | - |
| (0, 5), spawn | Succeeded | 24.3 s | 0.18 m, 2.5° |

The goal tolerance is 0.15 m and 0.15 rad.

**Demo video:** [`media/navigation_demo.mp4`](../media/navigation_demo.mp4). It runs slower than real time because the machine used software rendering.

## Challenges

- **Different ROS and Gazebo version:** the Classic plugins, world, spawn and topics had to be ported to Gazebo Sim.
- **Room and map did not match:** the room pose in the world's saved state block differed from its model pose by about 1.25 m. The state block pose matched the map.
- **Odometry error on turns:** the base frame was not at the wheel centre and the wheel separation was wrong.
- **Slow simulation:** without GPU acceleration, the simulation ran at about 0.5 times real time with the Gazebo and RViz windows open.
- **RViz jitter:** caused by HiDPI scaling on a high-DPI screen. Turning it off fixed it.
- **Lifecycle timeout:** once, under full CPU load, the planner's lifecycle reply timed out and navigation stayed inactive. Relaunching `navigation.launch.py` is the workaround. CycloneDDS, suggested in `help.md`, was not tested.

## Limitations

- Not tested: moving obstacles, and localization from a completely unknown position.
- Only `NavigateToPose` is configured.
- Stopping close to obstacles relies on the controller's collision check. There is no collision monitor.

# testbed_navigation

Map loading, localization and navigation for Testbed-T1.0.0, built from individual Nav2 nodes without calling `nav2_bringup`.

## Structure

| File | Purpose |
|---|---|
| `launch/map_loader.launch.py` | `map_server` and its lifecycle manager |
| `launch/localization.launch.py` | `amcl` and its lifecycle manager |
| `launch/navigation.launch.py` | Planner, controller, behavior, BT navigator and velocity smoother servers with their lifecycle manager |
| `config/map_server_params.yaml` | Map server parameters |
| `config/amcl_params.yaml` | AMCL parameters |
| `config/nav2_params.yaml` | Navigation and costmap parameters |


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

## Challenges

- **Room and map did not match:** the room pose in the world's saved state block differed from its model pose by about 1.25 m. The state block pose matched the map.
- **Odometry error on turns:** the base frame was not at the wheel centre and the wheel separation was wrong.
- **Slow simulation:** without GPU acceleration, the simulation ran at about 0.5 times real time with the Gazebo and RViz windows open.
- **RViz jitter:** caused by HiDPI scaling on a high-DPI screen. Turning it off fixed it.
- **Lifecycle timeout:** once, under full CPU load, the planner's lifecycle reply timed out and navigation stayed inactive. Relaunching `navigation.launch.py` is the workaround. 



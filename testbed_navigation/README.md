# testbed_navigation

## Purpose

Provides modular Nav2 map loading, AMCL localization, and autonomous navigation for the testbed robot in Gazebo Classic.

## Files

- `launch/map_loader.launch.py`: starts the static map server and its lifecycle manager.
- `launch/localization.launch.py`: starts AMCL and its lifecycle manager.
- `launch/navigation.launch.py`: starts the Nav2 planning, control, behavior, and behavior-tree navigation servers with a separate lifecycle manager.
- `config/amcl_params.yaml`: AMCL and localization parameters.
- `config/nav2_params.yaml`: planner, controller, behavior, costmap, and BT navigator parameters.

## Nodes and Plugins

- `nav2_map_server`: publishes the configured static map.
- `nav2_amcl`: uses `DifferentialMotionModel` and the `likelihood_field` laser model.
- `planner_server`: uses `nav2_navfn_planner/NavfnPlanner`.
- `controller_server`: uses DWB (`dwb_core::DWBLocalPlanner`).
- `behavior_server`: provides spin, backup, drive-on-heading, and wait behaviors.
- `bt_navigator`: runs the default `NavigateToPose` behavior tree.
- Three separate lifecycle managers control map loading, localization, and navigation independently for modularity.

## Run

Use the workspace's Cyclone DDS configuration and start each launch in a separate terminal, in this order:

```bash
source /opt/ros/humble/setup.bash
source ~/assignment_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=37
export CYCLONEDDS_URI=file://$HOME/cyclonedds.xml
~/rkill.sh
```

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
ros2 launch testbed_navigation navigation.launch.py
```

- Bringup without its RViz: `ros2 launch testbed_bringup testbed_full_bringup.launch.py use_rviz:=false`
- Then start RViz last: `ros2 launch testbed_navigation rviz.launch.py`

## Test Results

Localization (AMCL vs Gazebo ground truth):
- 0.02 m at spawn, 0.17 m after a slow 360° spin, 0.26 m after a fast 360° spin.

Navigation (NavigateToPose, true pose from Gazebo), two clean-start cycles:
| Cycle | Goal | Result | Final pose | Error | Recoveries |
|---|---|---|---|---|---|
| 1 | (2.0, 5.0) same room | SUCCEEDED | (1.80, 4.98) | 0.20 m | 0 |
| 1 | (6.0, 7.0) same room | SUCCEEDED | (5.93, 6.91) | 0.11 m | 0 |
| 1 | (3.6, -2.0) through doorway | SUCCEEDED | (3.69, -1.91) | 0.13 m | 1 |
| 1 | (0.0, 5.0) home | FAILED (timeout) | (0.26, 4.91) | 0.28 m | 21 |
| 2 | (2.0, 5.0) same room | SUCCEEDED | (1.80, 4.95) | 0.21 m | 0 |
| 2 | (6.0, 7.0) same room | SUCCEEDED | (5.86, 6.90) | 0.17 m | 0 |
| 2 | (3.6, -2.0) through doorway | SUCCEEDED | (3.69, -1.91) | 0.13 m | 5 |
| 2 | (0.0, 5.0) home | SUCCEEDED | (-0.01, 4.87) | 0.13 m | 4 |

7/8 goals reached. The one failure was intermittent TF starvation after ~5 min of operation
(controller stopped receiving map->odom; see Known Issues).

Demo: see media/ (video + screenshots).

## Known Issues

- Intermittent TF starvation: under /tf load the controller_server can stop receiving AMCL's map->odom
	("Transform data too old when converting from map to odom", transform time frozen). Lowering the
	diff-drive update_rate from 100 to 30 Hz (/tf ~330 -> ~116 msg/s) fixed it in most runs; it recurred
	once after ~5 min. Workaround: restart the stack (~/demo_start.sh).
- RViz on Intel integrated graphics can briefly show "not responding" while building map/costmap textures
	at startup. Start RViz last (rviz.launch.py) and, if needed: gsettings set org.gnome.mutter check-alive-timeout 60000

## Challenges

- Lab LAN: default DDS domain shared with other PCs caused cross-talk and network drops that killed AMCL's lifecycle bond. Fixed with Cyclone DDS bound to loopback (multicast enabled) and `ROS_DOMAIN_ID=37`.
- `ROS_LOCALHOST_ONLY` with Cyclone limits participants (~10) -> Nav2 nodes failed "free participant index". Replaced with a Cyclone XML config.
- `pkill -f ros2` does not kill node processes; leftover lifecycle managers caused map_server to hang unconfigured. Use `~/rkill.sh`, which matches `--ros-args`.
- Lifecycle bonds timed out under load -> set `bond_timeout: 0.0`.
- /tf flood (diff-drive at 100 Hz, odom + 2 wheel TFs) starved the controller's TF listener -> robot drove past goals. Fixed with update_rate 30.
- Repeated force-killing of the Gazebo GUI left unkillable (D-state) processes; required a reboot. Close gzclient normally.

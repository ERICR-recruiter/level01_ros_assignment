# testbed_navigation

Manual Nav2 workflow for the **Testbed-T1.0.0** robot (ROS 2 Humble, Gazebo Classic 11).
Instead of calling `nav2_bringup`, each Nav2 component is started from its own launch file
and its own parameter file, so every stage can be tested on its own.

| Stage | Launch file | Parameter file | Nodes |
|---|---|---|---|
| Map loading | `launch/map_loader.launch.py` | `config/map_server_params.yaml` | `map_server`, `lifecycle_manager_map` |
| Localization | `launch/localization.launch.py` | `config/amcl_params.yaml` | `amcl`, `lifecycle_manager_localization` |
| Navigation | `launch/navigation.launch.py` | `config/nav2_params.yaml` | `controller_server`, `planner_server`, `behavior_server`, `bt_navigator`, `lifecycle_manager_navigation` |
| Everything + RViz | `launch/full_navigation.launch.py` | (the three above) | includes the three launch files and RViz |

RViz layout with the map, costmaps, plans and particle cloud: `rviz/navigation.rviz`.

## Build

```bash
mkdir -p ~/assignment_ws/src && cd ~/assignment_ws/src
git clone <your-fork-url>
cd ~/assignment_ws
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-gazebo-ros-pkgs \
                 ros-humble-xacro ros-humble-rmw-cyclonedds-cpp
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp     # recommended in help.md
```

(`nav2_bringup` is installed only for its dependencies and RViz plugins; none of its launch files are used.)

## Run - step by step (separate terminals, each with the workspace sourced)

```bash
# 1. Simulation: Gazebo + robot + RViz (robot spawns at x=0, y=5)
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# 2. Map
ros2 launch testbed_navigation map_loader.launch.py
#    check: ros2 lifecycle get /map_server   -> active
#           ros2 topic echo /map --once      -> 405 x 400 grid, resolution 0.05

# 3. Localization
ros2 launch testbed_navigation localization.launch.py
#    check: ros2 lifecycle get /amcl          -> active
#           ros2 run tf2_ros tf2_echo map odom -> transform near (0, 5)

# 4. Navigation
ros2 launch testbed_navigation navigation.launch.py
#    check: ros2 action list                  -> /navigate_to_pose
```

Or start 2-4 together (plus an RViz window with the navigation layout):

```bash
ros2 launch testbed_navigation full_navigation.launch.py
```

To open the navigation RViz layout from the second terminal, use the bringup RViz window and
set **Fixed Frame = map**, or run `full_navigation.launch.py` (which opens `rviz/navigation.rviz`).
Add `rviz:=false` to that launch file if you only want to use the bringup RViz.

### Sending a goal

* RViz: click **2D Pose Estimate** if the particles are not around the robot, then
  **2D Goal Pose** and click on the map (publishes `/goal_pose`, which `bt_navigator` turns into a
  `NavigateToPose` action).
* Terminal:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 5.0}, orientation: {w: 1.0}}}}" --feedback
```

## Design / approach

**Map loading** - `nav2_map_server` is a lifecycle node, so it is paired with its own
`nav2_lifecycle_manager` (`autostart: true`). The map defaults to
`testbed_bringup/maps/testbed_world.yaml` and can be replaced with `map:=/abs/path.yaml`.

**Localization** - AMCL with the likelihood-field laser model and the differential motion model.
`scan_topic` is `scan` (the Gazebo ray sensor), frames are `map` / `odom` / `base_footprint`
(the frame the diff-drive plugin publishes odometry for). The Gazebo world and the map share the
same origin, so the initial pose in `amcl_params.yaml` is the spawn pose (x=0, y=5, yaw=0) and
`set_initial_pose: true` localizes the robot immediately. `laser_max_range` matches the (fixed) 10 m
lidar range.

**Navigation** - only the basic pieces are used:

* `planner_server` - `NavfnPlanner` (Dijkstra) on the global costmap
  (static layer + obstacle layer + inflation layer).
* `controller_server` - `DWBLocalPlanner` on a 3 m x 3 m rolling local costmap
  (obstacle layer + inflation layer); publishes `/cmd_vel` straight to the Gazebo diff-drive plugin.
* `behavior_server` - spin, backup, drive-on-heading and wait recoveries.
* `bt_navigator` - Nav2's default behaviour tree (`navigate_to_pose_w_replanning_and_recovery`).
* One lifecycle manager per stage; the navigation one brings the servers up before `bt_navigator`.

The robot footprint in both costmaps is a polygon taken from the bounding box of `base_link.stl`
(plus 3 cm), because the robot is not centred on `base_footprint`.
`collision_monitor` and `velocity_smoother` were left out on purpose (basic navigation only);
they can be added as two more nodes and `node_names` entries.

## Challenges

* The starter code contained several bugs (wrong map path, missing install rules, a ROS 1 Gazebo
  plugin, a 1.5 m lidar range, ...). They are listed in `../BUGS_FOUND_AND_FIXED.txt`.
* Sim time must be on for every node, including `robot_state_publisher`, otherwise TF lookups time out.
* Each lifecycle manager only manages its own stage, so the stages can be started/stopped independently.
* If `bt_navigator` reports that it cannot load a BT plugin library, remove that name from
  `plugin_lib_names` in `nav2_params.yaml` (the list matches the Humble default).
* If goals time out, use Cyclone DDS (see `help.md`).

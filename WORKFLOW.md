# How to run the navigation setup

Tested on Ubuntu 22.04 (WSL2), ROS2 Humble, Gazebo Classic 11. Use one terminal per
step, and run `source /opt/ros/humble/setup.bash && source ~/assignment_ws/install/setup.bash`
in each new terminal.

## 0. Build (once, and after any change)
```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
export GAZEBO_MODEL_DATABASE_URI=""   # stops Gazebo hanging on "Preparing your world"
```

## 1. Simulation
```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
Wait until the robot appears in Gazebo and RViz opens. The robot spawns at (0, 5).

## 2. Map and localization
```bash
ros2 launch testbed_navigation localization.launch.py
```
This starts `map_server` and AMCL, so no separate map launch is needed.
Check: `ros2 lifecycle get /amcl` and `/map_server` should say `active [3]`.

## 3. Set the initial pose
AMCL waits for a pose before it publishes the `map` frame. Send the spawn pose:
```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 5.0}, orientation: {w: 1.0}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.0685]}}"
```
In RViz set **Fixed Frame** to `map` and add a Map display on `/map` (Durability: Transient Local).
The red laser points should sit on the map walls.

## 4. Navigation
```bash
ros2 launch testbed_navigation navigation.launch.py
```
Check that `controller_server`, `planner_server`, `behavior_server` and `bt_navigator`
are all `active [3]` (`ros2 lifecycle get /<name>`).

## 5. Send a goal
Click **Nav2 Goal** in RViz, or:
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
 "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: -4.4}, orientation: {w: 1.0}}}}" --feedback
```
Other goals that worked: (-6.5, 4.0) and (7.95, -5.3).

## Stopping and restarting
Press Ctrl+C in each terminal and wait for the prompt. If Gazebo gets stuck on the next
start, kill leftover processes and relaunch:
```bash
killall -9 gzserver gzclient rviz2 2>/dev/null; pkill -9 -f "ros2 launch"
```

## Common problems
| Symptom | Fix |
|---|---|
| "Timed out waiting for transform ... to map" | Localization isn't running or no initial pose yet (step 3) |
| RViz Map says "No map received" | Untick and re-tick the Map display; set its Durability to Transient Local |
| AMCL keeps asking for an initial pose | Publish step 3 with `frame_id: map`, not `odom` |
| `bt_navigator` fails to activate | `plugin_lib_names` in `nav2_params.yaml` is missing a BT plugin |

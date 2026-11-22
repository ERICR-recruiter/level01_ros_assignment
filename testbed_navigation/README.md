# Testbed navigation

This ROS 2 Humble package runs the navigation stages independently. The map
server publishes the supplied playground map. AMCL matches the simulated laser
scan to that map and publishes the map-to-odom transform. NavFn plans a path and
DWB follows it using the local laser costmap. The behavior tree requests a path
and then follows it. The first target for verification is a nearby goal in
clear space. Each launch starts its own lifecycle manager.

## Build

From the root of a workspace containing this repository under `src/`:

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

## Run in Gazebo and RViz

In each terminal below, source `/opt/ros/humble/setup.bash` and the workspace's
`install/setup.bash` first. Leave each launch running in its own terminal.

1. Run `ros2 launch testbed_bringup testbed_full_bringup.launch.py`.
2. Run `ros2 launch testbed_navigation map_loader.launch.py`. In RViz, set
   **Fixed Frame** to **map** and add a **Map** display on `/map`. Set its durability
   to **Transient Local** so it can receive the existing map.
3. Run `ros2 launch testbed_navigation localization.launch.py`. Use **2D Pose
   Estimate** to initialize near the Gazebo spawn at x=0, y=5, facing +x.
   Confirm the robot and laser scan align with the map. If needed, add a
   **LaserScan** display on `/scan` with **Best Effort** reliability.
4. Run `ros2 launch testbed_navigation navigation.launch.py`. Check
   `ros2 lifecycle get /bt_navigator` reports **active**. Add a **Path** display
   on `/plan` and use **2D Goal Pose** to send a nearby goal in free space.
   The RViz tool publishes to `/goal_pose`, which the Humble navigator
   receives. Watch the robot follow the path and stop at the goal.

Use `ros2 run tf2_ros tf2_echo map base_footprint` to check localization.
If a launch fails, check that its lifecycle nodes are active and that
`/clock`, `/odom`, and `/scan` are publishing. See the repository root's
`bugs_fixed.txt` for the starter-code fixes.

## Simulation evidence

Add screenshots or a short video here after verifying localization and goal
completion in your simulation.

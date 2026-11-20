# Testbed navigation on ROS 2 Humble

This package launches the Testbed’s map server, AMCL, and navigation servers
independently. The simulation runs in Gazebo Classic 11.10.2. Each group has
its own lifecycle manager, which configures and activates the nodes in that
group.

## Build

Run these commands from the workspace root. The repository belongs under
`~/assignment_ws/src/level01_ros_assignment`.

```bash
sudo apt install gazebo ros-humble-gazebo-ros-pkgs ros-humble-navigation2 \
  ros-humble-xacro ros-humble-joint-state-publisher
builtin source /opt/ros/humble/setup.bash
cd ~/assignment_ws
colcon build --symlink-install
```

In each terminal used below, load ROS and the workspace.

```bash
builtin source /opt/ros/humble/setup.bash
builtin source ~/assignment_ws/install/local_setup.bash
```

## Run and verify

1. Start the simulator and the navigation RViz view.

   ```bash
   ros2 launch testbed_bringup testbed_full_bringup.launch.py \
     rvizconfig:="$(ros2 pkg prefix --share testbed_navigation)/rviz/navigation.rviz"
   ```

2. Start the map server in a separate terminal.

   ```bash
   ros2 launch testbed_navigation map_loader.launch.py
   ```

   RViz should display the playground from `/map`. `ros2 lifecycle get
   /map_server` should report `active`. The default map is resolved from the
   installed `testbed_bringup` package. The `map` launch argument can select
   another map YAML.

3. Start AMCL in another terminal.

   ```bash
   ros2 launch testbed_navigation localization.launch.py
   ```

   Use **2D Pose Estimate** in RViz. For the stock spawn, click near `(0, 5)`
   in the map and point the arrow along positive X, to the right in the
   supplied top-down view. The approximate pose is visible in Gazebo. Wait
   for the lidar returns and the robot pose to appear on the map. Check the
   transform with `ros2 run tf2_ros tf2_echo map base_footprint`.

   If RViz shows `Frame [map] does not exist` while the map server and AMCL
   are active, set the initial pose. AMCL publishes the `map → odom`
   transform after it accepts the estimate.

4. Start navigation in another terminal.

   ```bash
   ros2 launch testbed_navigation navigation.launch.py
   ```

   Use **Nav2 Goal** in RViz to place a goal in free space, or send an action
   goal from a sourced terminal. The following goal is near the stock spawn.

   ```bash
   ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
     '{pose: {header: {frame_id: map}, pose: {position: {x: 1.2, y: 5.0}, orientation: {w: 1.0}}}}' \
     --feedback
   ```

   From there, a goal near `(-4.3, 2.3)` exercises planning around the wall
   at `x ≈ -3`. Check that the action succeeds and the robot stops at the
   destination.

## Configuration and results

- `config/map_server_params.yaml` defines the `map` frame and `/map` topic.
  The map contains 405 × 400 cells at 0.05 m per cell.
- `config/amcl_params.yaml` uses the differential-drive motion model and
  `/scan`. AMCL supplies `map → odom`, and Gazebo supplies
  `odom → base_footprint`. Both use Gazebo time.
- `config/nav2_params.yaml` configures the NavFn global planner, the DWB
  local controller, and the plugins used by Humble’s navigation behavior
  trees. The global costmap combines the saved map with lidar observations.
  The local costmap follows the robot in `odom`. Both use a rectangular
  footprint estimated from the robot meshes.
- The original map referenced a nonexistent image and was missing from the
  installed package. The original 1.5 m lidar limit produced no finite
  returns at the default spawn. The repaired map published successfully,
  and an 8 m lidar limit gave AMCL observations at spawn. See the
  [starter bug log](../STARTER_BUG_FIXES.txt) for the fixes and measurements.

## Demo checks

- For localization, capture the AMCL pose and lidar returns aligned with the
  occupancy map in RViz.
- For navigation, capture the active goal and the green plan around the wall.
  The two action goals succeeded in the verification run, with final position
  errors of 0.200 m and 0.173 m.

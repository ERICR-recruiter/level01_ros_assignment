# ERIC Robotics Level 1 ROS 2 Navigation Assignment

A ROS 2 Humble / Gazebo Classic navigation workspace for Testbed-T1.0.0. The
repository preserves the supplied robot and world, fixes verified starter
issues, and adds a manual Nav2 stack without using `nav2_bringup`.

## Packages

- `testbed_description`: robot model, meshes, sensor plugins, and RViz files.
- `testbed_gazebo`: Gazebo Classic worlds, models, and spawning launches.
- `testbed_bringup`: full simulator/RViz launch and supplied static map.
- `testbed_navigation`: independent map-server, AMCL, and Nav2 launches.

## Dependencies

Ubuntu 22.04, ROS 2 Humble, Gazebo Classic 11, RViz2, `gazebo_ros`, `xacro`,
and Nav2. Install declared dependencies with:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

## Build

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Launch

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
ros2 launch testbed_navigation navigation.launch.py
```

Run the first command, then map loading, localization, and navigation in
separate terminals. Use RViz 2D Pose Estimate before sending a 2D Goal Pose.

## Architecture

Gazebo publishes `/scan`, `/odom`, and `odom -> base_footprint`; AMCL consumes
the map/scan/odometry and publishes `map -> odom`; Nav2 plans and controls via
`/cmd_vel`. The navigation launch starts map-independent planner, controller,
BT Navigator, behavior server, and lifecycle manager nodes directly.

Use `testbed_navigation/rviz/navigation.rviz` for the map, TF, robot, scan,
AMCL pose, costmaps, paths, and goal tools.

## Testing and limitations

Static Python/YAML/XML validation has been performed. Starter simulation,
scan, odometry, TF, and `/cmd_vel` were observed in a remote Humble/Gazebo
Classic environment. AMCL and end-to-end navigation remain runtime validation
items; see `testbed_navigation/README.md` and `BUG_FIXES.md`.

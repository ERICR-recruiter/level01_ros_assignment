# Testbed Navigation — ROS 2 Humble

This package implements the Testbed-T1.0.0 navigation workflow with individual Nav2 lifecycle nodes and plugin servers. It intentionally does **not** use the `nav2_bringup` launch files.

## Target environment

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic 11
- RViz2
- Nav2 packages for Humble

## Package layout

```
testbed_navigation/
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
├── launch/
│   ├── full_navigation_bringup.launch.py
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
├── CMakeLists.txt
└── package.xml
```

## Build

From the assignment workspace:

```bash
cd ~/work
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Start simulation, map server, and localization

Run this in Terminal 1:

```bash
source /opt/ros/humble/setup.bash
source ~/work/install/setup.bash
ros2 launch testbed_navigation full_navigation_bringup.launch.py
```

This combined launch starts:
- Gazebo playground and the Testbed robot
- Robot State Publisher
- RViz2 with `full_bringup.rviz`
- Nav2 Map Server, managed by the localization lifecycle manager
- AMCL, managed by the same lifecycle manager

Wait for Gazebo to load and the robot to spawn. The Map display in RViz subscribes to `/map`; the Fixed Frame is configured as `map`. Once the map appears, use **2D Pose Estimate** to initialize the robot's pose. The robot is spawned at approximately x=0, y=5 in the supplied world; use its actual position visible in Gazebo/RViz rather than blindly accepting this estimate.

Do not start `localization.launch.py` or `map_loader.launch.py` separately while the combined launch is running: that would create a second `map_server` node with the same name.

## Start navigation servers

After the map and AMCL are active and the initial pose is set, run this in Terminal 2:

```bash
source /opt/ros/humble/setup.bash
source ~/work/install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```

In RViz2, use **2D Goal Pose** to send a goal in free space. The robot should plan around obstacles and drive toward the goal.

## Modular debugging launches

For debugging individual components, the launches remain independently available:

- Simulation only: `ros2 launch testbed_bringup testbed_full_bringup.launch.py`
- Map Server only: `ros2 launch testbed_navigation map_loader.launch.py`
- Map Server + AMCL: `ros2 launch testbed_navigation localization.launch.py`

Run only one map-server launch at a time. Stop the combined launch before using either isolated map/localization launch.

## Important interfaces

- Map: `/map`
- Laser scan: `/scan`
- Odometry: `/odom`
- Localization estimate: `/amcl_pose`
- Main navigation action: `/navigate_to_pose`
- TF chain: `map -> odom -> base_footprint -> base_link`

## Diagnostic commands

```bash
ros2 node list
ros2 lifecycle nodes
ros2 topic list
ros2 topic info /map
ros2 topic echo /map --once
ros2 topic echo /amcl_pose
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 action list
ros2 run tf2_tools view_frames
```

Expected navigation actions include `/navigate_to_pose`, `/compute_path_to_pose`, and `/follow_path`.

## Tuning notes

The supplied simulated LiDAR publishes a LaserScan on `/scan` with a configured range of 0.10–1.50 m. The obstacle-layer ranges and AMCL laser range are therefore kept within that sensor range. The initial DWB velocity limits are deliberately conservative for first simulation tests.

These parameters are a starting configuration, not a claim of verified performance. Confirm scan rate, odometry, TF, map alignment, costmaps, and safe goal locations on the target computer. Adjust the robot radius and planner/controller settings only after inspecting the simulation.

## Testing record

Record the actual Ubuntu/ROS 2 versions, build output, launch results, goal coordinates, and any errors encountered during the friend-computer test. Add genuine screenshots or a short video after successful localization and navigation. Runtime success must be confirmed on the target ROS 2 Humble computer.

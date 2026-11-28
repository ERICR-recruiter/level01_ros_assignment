# testbed_navigation

This package builds the basic Nav2 workflow directly from the ROS 2 Humble
servers and plugins. It does not launch `nav2_bringup`.

## Components

- `map_loader.launch.py` starts `nav2_map_server` and its lifecycle manager.
- `localization.launch.py` starts AMCL and a separate lifecycle manager.
- `navigation.launch.py` starts the planner, controller, behavior, and BT
  navigator servers with a lifecycle manager.
- `config/` contains the map server, AMCL, DWB controller, NavFn planner,
  obstacle/static/inflation costmaps, behavior plugins, and BT plugin settings.

The map uses the included `testbed_world.yaml`. AMCL and costmaps subscribe to
the robot's `/scan`; navigation uses `/odom`, `map`, `odom`, and
`base_footprint`, matching the supplied robot description and Gazebo drive
plugin.

## Build and run

From the workspace root:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Start the simulation, map server, and localization in separate terminals:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
```

AMCL is seeded with the Gazebo spawn pose `(0, 5, 0)` and should establish
`map → odom` when the map and scan are available. This assumes the map and
Gazebo world are aligned. If the actual pose differs (for example, after
moving the robot or restarting AMCL), set its current pose with RViz's **2D
Pose Estimate** tool after map and localization are active. Then start
navigation in another terminal:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Use RViz's **2D Goal Pose** tool to send a `NavigateToPose` goal. The launch
files use simulation time by default; set `use_sim_time:=false` only when
running without simulated `/clock`.
The map can be overridden with `map:=/absolute/path/to/map.yaml`; the behavior
tree can be overridden with `bt_xml:=/absolute/path/to/tree.xml`.

## Design and verification notes

Map loading, localization, and navigation have independent launches and
lifecycle managers, so each stage can be started and inspected separately.
The map server must be active before AMCL; localization and the map must be
active before sending navigation goals. NavFn and DWB provide a compact
2D-planning setup for the supplied differential-drive base.

The starter fixes are listed in the repository-root `BUG_FIXES.txt`. All four
packages build on ROS 2 Humble. End-to-end localization, goal motion, and
screenshots have not been verified for this submission and require an
interactive Gazebo session.

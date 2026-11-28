# Testbed-T1.0.0 ROS 2 Navigation Assignment

This repository contains the Testbed-T1.0.0 Gazebo simulation and a modular
`testbed_navigation` package for map loading, AMCL localization, and Nav2
navigation on ROS 2 Humble. Navigation servers are launched directly; this
submission does not use `nav2_bringup`.

## Build

From the workspace root:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Run

Start each command in a separate terminal after sourcing the workspace:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
```

The Gazebo spawn launch places the robot at `(x=0, y=5, yaw=0)`, which is
configured as AMCL's startup pose. This assumes the map and Gazebo world are
aligned. If the robot has moved or starts elsewhere, use RViz's **2D Pose
Estimate** to set its current pose after map and localization are active.
Then start navigation:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Use RViz's **2D Goal Pose** tool to request a `NavigateToPose` goal. Full
end-to-end localization and goal motion have not been verified for this
submission. See [testbed_navigation/README.md](testbed_navigation/README.md)
for package details and [BUG_FIXES.txt](BUG_FIXES.txt) for the identified
starter-code fixes.

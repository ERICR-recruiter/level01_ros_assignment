# Run Instructions — ROS 2 Humble Navigation

Tested on Ubuntu 22.04, ROS 2 Humble, Gazebo Classic 11 and Nav2.

## Build
```bash
cd ~/assignment_test_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Launch

Follow the seven-terminal Verified Launch Procedure in README.md.
It starts Gazebo, robot description, robot spawning, map server, AMCL, Nav2 and RViz separately.

Use Cyclone DDS consistently in every terminal:
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

## Navigation

1. Set the initial robot pose using RViz 2D Pose Estimate.
2. Select a reachable destination using 2D Goal Pose.
3. Observe the planned path and robot movement in Gazebo and RViz.
4. Verify that the robot reaches the destination and stops.

## Verification

Run the lifecycle verification commands in README.md.
See TEST_REPORT.md for runtime results and evidence/ for screenshots and the demonstration video.

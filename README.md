# Level 1 - ROS 2 Navigation Assignment - [Sameer Patwardhan-(sam-airobotics)]

This repository contains the Level 1 navigation solution for the ERIC Robotics
Testbed...

The approach was to first make the starter simulation reliable, then build the
navigation stack in separate stages so each part could be tested independently...

![ROS 2 navigation pipeline](docs/ros2_navigation_pipeline.svg)

## Environment...

The assignment targets Ubuntu 22.04, ROS 2 Humble, Gazebo Classic, and RViz2...

## Build...

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/sam-airobotics/level01_ros_assignment.git .

cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Start the testbed...

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

Run Gazebo and RViz as the normal desktop user...
Using a root shell can cause X11 display errors...

## Check the robot...

```bash
ros2 topic list
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_footprint
```

The expected navigation TF chain is:

```text
map -> odom -> base_footprint -> base_link -> lidar_link_1
```

![Testbed TF tree](docs/testbed_tf_tree.svg)

## Load the map...

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

Check the map...

```bash
ros2 topic echo /map --once
ros2 lifecycle get /map_server
```

## Start localization...

```bash
ros2 launch testbed_navigation localization.launch.py
```

Then set an initial pose in RViz with **2D Pose Estimate**...

Check AMCL...

```bash
ros2 lifecycle get /amcl
ros2 topic echo /amcl_pose --once
```

## Start navigation...

```bash
ros2 launch testbed_navigation navigation.launch.py
```

The custom launch starts the planner, controller, behavior server, BT navigator,
waypoint follower, and lifecycle manager directly...

The planner uses NavFn...
The controller uses regulated pure pursuit...

## Send a goal...

```bash
ros2 action list | grep navigate_to_pose
```

A basic CLI test...

```bash
ros2 action send_goal /navigate_to_pose   nav2_msgs/action/NavigateToPose   "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5, z: 0.0}, orientation: {w: 1.0}}}}"   --feedback
```

Choose a reachable point in the mapped free space...

## Debugging...

```bash
ros2 node list
ros2 action list
ros2 topic echo /cmd_vel
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 run tf2_tools view_frames
```

Useful lifecycle checks...

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /bt_navigator
```

## Assignment constraint...

The solution does not use a `nav2_bringup` launch file as the navigation
stack itself...
The required Nav2 nodes are launched explicitly from `testbed_navigation`...

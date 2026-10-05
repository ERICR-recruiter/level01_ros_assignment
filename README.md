# testbed_navigation

This is my submission for the Level 1 ROS2 assignment.
In this project, I used my own launch files and parameter files to run the map server, AMCL and Nav2 navigation. I did not use nav2_bringup.

I tested it using ROS2 Humble and Gazebo Classic inside a Docker container.

Name: Ved Oswal  
Email: oswalved8055@gmail.com
Phone: 8446341273

Demo Video: https://drive.google.com/drive/folders/1nh6JUvCivguaboWzS_PHiCGLDF0eE4y_

## Files

launch/map_loader.launch.py - Starts the map server
launch/localization.launch.py - Starts AMCL
launch/navigation.launch.py - Starts the Nav2 navigation nodes
config/amcl_params.yaml - AMCL settings
config/nav2_params.yaml - Nav2 settings
rviz/nav.rviz - RViz configuration

I used a separate lifecycle manager in each launch file so I could test them separately.

## How to Run

First build the workspace:
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash

Then run these commands in separate terminals:
ros2 launch testbed_bringup testbed_full_bringup.launch.py
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
ros2 launch testbed_navigation navigation.launch.py

After this, I can send a goal using 2D Goal Pose in RViz.
I can also send a goal from the terminal:
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 5.0}, orientation: {w: 1.0}}}}" --feedback


## Bugs in the Starter Code

I found 4 bugs in the starter code.
They are listed in `BUGS.txt`.
The bugs were:
Missing `()` in `CMakeLists`
Maps folder was not installed
Wrong map image name
Extra `>` in the Gazebo file

# Problems I Faced

## 1. AMCL was drifting

At first, AMCL was around **2.4 m away** from the real robot position.
I changed the odometry noise and LiDAR range settings.
After that, AMCL was around **15 cm away** from the real robot position in my test.

## 2. Robot was moving left and right

The robot was zig-zagging while moving.
When I checked `/cmd_vel`, the angular velocity was changing between:
(+1.0,-1.0)

I changed:
max_vel_theta
acc_lim_theta
forward_point_distance
After that, the robot's turning became smoother.

## 3. Robot was getting stuck at doors

The doors are around **0.9 m wide**.
My first inflation settings did not leave enough space for the robot.
I reduced the robot radius and inflation radius and also changed the progress checker.
This helped the robot pass the doors better.

### 6. Warnings in the simulation

I got warnings like:
Behavior Tree tick rate was exceeded
and
Message Filter dropping message

The simulation was running slower than real time on my laptop.

I increased:

bt_loop_duration
costmap transform_tolerance
This reduced the problem a little, but the warnings were still sometimes present.

## Results

- Map loads correctly: Yes
- Map matches Gazebo: Yes
- AMCL tracking: Around 15 cm
- Goal in the same room: Reached
- Goal through a door: Yes
- Obstacle avoidance: Yes

## Limitations
Sometimes the robot gets stuck or moves back and forth near narrow doors.

I think this happens because:
The LiDAR range is only 1.5 m
The robot does not get much LiDAR information near the doors
The doors are only a little wider than the robot
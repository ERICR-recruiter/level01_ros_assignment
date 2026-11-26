# testbed_navigation

This package lets the testbed robot find its place on a saved map and drive
to a goal using Nav2. I started every Nav2 node by hand in my own launch
files, without nav2_bringup.

## Files

- launch/map_loader.launch.py - loads the map
- launch/localization.launch.py - map server + AMCL
- launch/navigation.launch.py - planner, controller, behavior tree and the rest
- config/amcl_params.yaml, config/nav2_params.yaml - the settings
- behavior_trees/navigate_to_pose.xml - what the robot does when it is blocked
- media/ - screenshots

## How I run it

I use one terminal per step (and source ~/assignment_ws/install/setup.bash in each):

1. `ros2 launch testbed_bringup testbed_full_bringup.launch.py`
   If the robot is missing in Gazebo, run
   `ros2 launch testbed_gazebo spawn_testbed.launch.py`
2. `ros2 launch testbed_navigation localization.launch.py`
3. `ros2 launch testbed_navigation navigation.launch.py`
4. In RViz I set Fixed Frame to map, add the Map display, and click
   "2D Goal Pose" to send a goal.

## What I did

First I got the map to load with map_server. Then I added AMCL so the robot
knows where it is. It uses the lidar and the odometry from the Gazebo
drive plugin. The robot starts at (0, 5), so I gave AMCL that as the first
pose.

For navigation I used the NavFn planner and the Regulated Pure Pursuit
controller, because it is a simple choice for a robot with two drive wheels.
The behavior tree replans every second while the robot follows the path. If
it gets stuck it clears the costmaps, spins, waits and backs up. I also put
a velocity smoother between the controller and the robot so it speeds up
and slows down more gently.

## Problems I ran into

- The starter code had a few bugs (it would not build, the lidar only saw
  1.5 m, and some folders were not installed). They are in BUGS_FOUND.txt.
- AMCL was running but there was no map frame. It turned out Gazebo had
  crashed, so there was no robot and no odometry. Restarting and spawning
  the robot fixed it.
- Gazebo is slow to start on WSL, so the spawn step sometimes timed out. I
  ran the spawn launch file myself after Gazebo was up.
- The map did not show in RViz until I set the Map display's durability to
  Transient Local.
- bt_navigator failed to start because Nav2's default "navigate through
  poses" tree needed three more BT plugins. I added them to the plugin list.
- The robot kept driving after a single manual /cmd_vel command, so I had
  to send a zero command to stop it.

## Screenshots

- media/localization.png
- media/map_loaded.png
- media/navigation.png
- media/navigation_reached.png

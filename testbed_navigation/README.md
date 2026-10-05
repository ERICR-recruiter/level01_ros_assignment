# Testbed Navigation

This package launches Nav2 for the Testbed-T1.0.0 in three stages: map loading, AMCL localization, and navigation. Each stage has its own launch file and can be checked separately.

## Build

From the ROS 2 workspace root:

~~~bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
~~~

## Launch

Run each command in a separate terminal, sourcing install/setup.bash in each one.

1. Start Gazebo and the robot:

   ~~~bash
   ros2 launch testbed_bringup testbed_full_bringup.launch.py
   ~~~

2. Load the map:

   ~~~bash
   ros2 launch testbed_navigation map_loader.launch.py
   ~~~

3. Start localization:

   ~~~bash
   ros2 launch testbed_navigation localization.launch.py
   ~~~

   The default initial estimate is (0, 5, 0). Override it with initial_x, initial_y, and initial_yaw if the robot starts elsewhere.

4. Start navigation:

   ~~~bash
   ros2 launch testbed_navigation navigation.launch.py
   ~~~

Send a goal with RViz's 2D Goal Pose tool or from a terminal:

~~~bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 2.0}, orientation: {w: 1.0}}}}"
~~~

The map loader accepts a different map with map:=/path/to/map.yaml.

## Nodes and parameters

- map_loader.launch.py runs map_server and a lifecycle manager.
- `config/map_server_params.yaml` contains the map server defaults; the launch argument supplies the map path and simulation time setting.
- localization.launch.py runs AMCL and a lifecycle manager.
- navigation.launch.py runs planner_server, controller_server, behavior_server, bt_navigator, velocity_smoother, and their lifecycle manager.
- NavFn and Regulated Pure Pursuit handle planning and path following. The behavior trees include recovery actions.
- The planner and controller host the global and local costmaps.
- The costmaps use a measured rectangular footprint and the /scan topic.
- Collision Monitor is optional and is not part of this bringup.

## Evidence

The full workflow was run in Gazebo. The map, AMCL, and navigation nodes activated; goals at (3, 2) and (0, 5) completed successfully. Measured post-goal drift was about 0.036 m over three seconds.

The starter setup needed separate lifecycle-managed launch stages so each part could be started and checked independently. During simulation, wheel and caster contact settings caused the robot to drift, and the controller continued to publish nonzero velocity briefly after reaching a goal. Those issues were corrected and the stop behavior was measured again. The remaining model geometry limitation is recorded in the root `bugs.txt`.

![RViz navigation view](evidence/navigation_result.png)

[Gazebo navigation demo (20 seconds)](evidence/navigation_demo.mp4)

See the repository root bugs.txt for starter-code fixes and the remaining chassis-geometry limitation.

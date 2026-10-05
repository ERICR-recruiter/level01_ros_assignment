
# Testbed Navigation — Submission Notes

Hi! This is Rohanta Shaw's submission for the Level 1 ROS2 navigation assignment. Below is a quick rundown of what I built, the bugs I ran into, and what I got working.
## What I did

- Created a new package, testbed_navigation, that brings up the Nav2 stack by hand (no nav2_bringup), using the individual plugins:
        launch/map_loader.launch.py — loads the map with map_server.
        launch/localization.launch.py — map_server + amcl.
        launch/navigation.launch.py — planner, controller, behaviours, BT navigator and a velocity smoother.
        launch/bringup.launch.py — runs localization + navigation + RViz together.
- Config files:
        config/amcl_params.yaml — AMCL tuned for a differential drive robot, seeded at the robot's spawn pose so it localizes without a manual pose estimate.
        config/nav2_params.yaml — NavFn global planner, DWB local planner, recovery behaviours, costmaps and the velocity smoother.
    The key idea I leaned on: every Nav2 server is a lifecycle node, so each of my launch files pairs the nodes with a lifecycle_manager (autostart) that walks them through configure → activate.
    Found and fixed the intentional bugs in the starter code — full list with the fixes is in BUGS_FIXED.txt in the repo root.

## Bugs / errors I faced (and how I got past them)

- Map wouldn't load — the map YAML pointed at wrong_path_testbed_world.pgm, and the maps/ folder wasn't being installed. Fixed the filename and added maps to the install in CMakeLists.txt.
- Build failed on testbed_description — ament_package was written without (), so the package never registered. Added the brackets.
- Gazebo opened empty — the world launch argument was declared but never passed to Gazebo, so no walls loaded. Forwarded it in the launch file.
- colcon couldn't find ament_cmake — turned out I just hadn't sourced /opt/ros/humble/setup.bash in that terminal. Added it to my ~/.bashrc.
- AMCL kept dropping every laser scan ("timestamp earlier than the transform cache") — robot_state_publisher wasn't using sim time, so its TF timestamps were on wall-clock while the scans were on sim-clock. Set use_sim_time: True on it. This was the big one — localization only started working after this.
- Nodes kept going inactive mid-run on my machine — the lifecycle manager's heartbeat ("bond") was timing out when the CPU got busy. Set bond_timeout: 0.0 so it stops tearing nodes down, and bumped the costmap transform_tolerance. After that the stack stayed up.

## What I achieved

    Map loads correctly and shows in RViz.
    AMCL localizes the robot (laser lines up with the map walls).
    The robot plans and drives to navigation goals sent either from RViz (2D Goal Pose) or via the navigate_to_pose action — reaches the goal with SUCCEEDED.
    A short screen recording of localization + navigation is included with the submission.

# How to run

## Terminal 1 - simulator + robot
ros2 launch testbed_bringup testbed_full_bringup.launch.py

## Terminal 2 - localization
ros2 launch testbed_navigation localization.launch.py

## Terminal 3 - navigation
ros2 launch testbed_navigation navigation.launch.py

## RViz cmd in own terminal, then send a goal (example)
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: 2.0, y: 5.0}, orientation: {w: 1.0}}}}"

I would like to thank you for the learning opportunity and would love to discuss this further with the team.

For screenshots and images, please find them in this link: https://drive.google.com/drive/folders/1uxq2NlluEkq2t9zNRoNymOC0l8GnHbgI?usp=drive_link

Name: Rohanta Shaw Email: shawrohanta@gmail.com Phone No.: 9903998788

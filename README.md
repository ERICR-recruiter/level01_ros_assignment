# Level 1: ROS2 Navigation Assignment - Chaitanya Ahire

## Overview
At ERIC Robotics, we’re big believers in building software with modularity. The nav2 stack reflects this perfectly with flexible, plugin-based framework, allowing you to pick and choose which pieces you need and run them independently. In this assignment, you’ll walk through the navigation workflow step by step—manually creating and calling actions—to bring an autonomous robot to life.

**Here’s what to do:**
1. We have shared some starter code for the 'Testbed-T1.0.0', a simple open-source robot developed by the team here at ERIC Robotics. **Please note that there are some bugs intentionally left in the starter code that you will need to identify and fix. You also need to make a text file listing the bugs you were able to identify and how did you fix them and add that file in the root directory outside the navigation package** Your task is to develop a new ROS2 package called `testbed_navigation` to manage the navigation workflow for this robot.
2. However, rather than simply calling `nav2_bringup`, in this assignment you will manually build the required action components (i.e., using the `map_server`, `amcl`, `planner` plugins, and `bt_` plugins) to run ros2 navigation, by working directly with the respective `nav2` plugins.
3. i.e., In the `testbed_navigation` package, write individual launch files to load a map, perform localization, and navigate using the plugins provided by `nav2`.
4. Document your process so we can see how you tackled the task.

This assignment gives you hands-on experience with ROS2’s navigation plugins, while showcasing your ability to design modular and effective robotics solutions.

### Deadline & submissions
1. Four days (96 hrs) from the moment you accept the assignment.
2. All applicants should fork the repository for the assignment. To submit your code, after completion create a Pull Request (PR) back to the `main` branch. You can commit any number of times to your fork before your deadline.

## Repository Structure

```
ros_nav2_assignment/
├── testbed_description/
│   ├── launch/            # Launch the full base simulation
│   ├── meshes/
│   ├── rviz/            # RVIZ configuration files
│   └── urdf/            # URDF files for Testbed-T1.0.0
├── testbed_gazebo/
│   ├── worlds/            # Simulation world files
│   ├── launch/            # Launch files for Gazebo
│   └── models/            # Misc. Gazebo model files
├── testbed_bringup/
│   ├── launch/            # Launch file for bringing up the robot
│   └── maps/              # Predefined map of the test environment
├── help.md                # Guidelines and FAQs
└── README.md              # Instructions for the assignment
testbed_navigation/
├── CMakeLists.txt
├── package.xml
├── README.md
├── config/
│   ├── amcl_params.yaml          # AMCL (localization)
│   └── nav2_params.yaml          # planner, controller, costmaps, behaviors, BT, smoother
├── launch/
│   ├── map_loader.launch.py      # nav2_map_server + lifecycle manager
│   ├── localization.launch.py    # nav2_amcl + lifecycle manager
│   ├── navigation.launch.py      # Nav2 servers + lifecycle manager
└── rviz/
    └── navigation.rviz           # RViz preset (fixed frame = map)
```

## Assignment Objective
Your goals are to:
1. Learn how to configure and use ROS2 `nav2` plugins in independent files.
2. Set up manual map loading and localization for the given simulation environment.
3. Implement the required navigation plugins to handle robot navigation in the `testbed_navigation` package. Only basic navigational functionality is expected in this assignment, so choose your plugins accordingly.

## Requirements

To get started, you’ll need:
- ROS2 Humble installed. (Install from [Humble Installation](https://docs.ros.org/en/humble/Installation.html)) (You will need Ubuntu 22.04/Windows 10 for this. More in the help section.)
- Gazebo simulator (version 11.10.2 is compatible with ROS2 Humble) (Install from [Gazebo Installation](https://classic.gazebosim.org/tutorials?tut=install_ubuntu)) and Rviz simulator.
- Basic to intermediate knowledge of ROS2 navigation concepts.
- Familiarity with creating and managing ROS2 packages, actions, and parameter files.
- The reference documentation for the `nav2` stack is going to be your best friend for this assignment: [Nav2 Documentation](https://navigation.ros.org/).

A map was given in the workspace named testbed_world.pgm and we have to navigate and localize the robot model . After the simulation certain things that should be taken into consideration. They were

- Map Loading
- Localization
- Navigation

## Map loading
To laod a given map(testbed_world.pgm) in Rviz a launch file was made to configure and activate map server and two nodes were taken :
- map_server(nav2_map_server) : reads testbed_world.yaml + tested_world.pgm and publishes it on :/map
- lifecycle_manager_map : configure and activate map server
- the node published data on the topic named :/map

##Localization
describes where the robot is and AMCL is used to make gusses of the robot position on the maps and these guesses are called particles by giving and setting values and references the location is constantly updated to give the accurate location
What AMCL does
*AMCL finds where the robot is on the map.
*It makes many guesses of the robot's position. These guesses are called particles.
*Every time the robot moves, AMCL repeats three steps:
*Move all the guesses the same way the wheels say the robot moved, with a little randomness added.
*Check each guess: "If the robot were here, would the laser see the walls where the map has them?"
*Keep the good guesses and throw away the bad ones.
*After a few moves, all the guesses gather at the robot's real position.
*AMCL then publishes the link between the map and the robot's odometry (the map → odom transform). This corrects the small errors that wheel odometry builds up over time.
Many parameters and values were added in .yaml file to make localisation working these includes:
- Frame and topics  : added all frames that were required
- Starting position :set initial pose of the robot
- Motion settings   : include noise reduction caused by rotation, translation ,etc
- Range of lidar was also updated

##Navigation
Navigation actually means how will i reach the goal for that nav2 has certain plugins and main 5 nav2_servers to complete the process.They are as follows :
- bt_navigator :recieves the goal and decide what to do
- planner_server :it is also called the map reader it draws the full route to the goal
- controller_server : it follows the route and send speed commands
##There are mainly two plugins for this DWD and Regulated Pure Pursuit
##We started with DWB, Nav2's classic controller. 
 - DWB imagines hundreds of possible short drives (different speeds and turns), throws away any that would hit something, and picks the best of the rest.
   The problem: in the 0.9 m doorways (robot width 0.42 m), almost all imagined drives clipped a wall. Only slow, careful ones were left, so the robot crept and wiggled through every door.
   Tuning DWB (shorter simulation time, smaller inflation) helped only a little.
 - RPP doesn't search at all. It just follows the planned path. Since the planner already routes the path through the centre of each door, RPP drives straight through at a steady speed.
   The trade-off: RPP doesn't steer around new obstacles. It slows or stops, and the planner re-plans. In this static test world, that's fine.
- behaviour_server : it rescues or avoid from collision by spining and backup or stop if required
- velocity_smoother :it limits the sudden speed change during path travelling and publishes on cmd_vel


##Challenges
- The ROS should use its own clock not the computer therefore we gave amcl file use_sim_time : true
- Gazebo crashed right after the robot spawned : so i spawe the robot after the gazebo published the /clock message to avaoid the crash
- base_footprint and wheel seperatio were wrong updated so it gave problem to laser scan  : so measured the meshes and moved the base_footprint
- RViz fixed frame was odom, due to which the goal was saved to odom with old timestamp , thats why after few second that time was no in TF buffer so the robot couldn't find the path and to     fixed it the fixed fram was changed to :/map
- Robot stopped at sharp corner so we gave different inflation for global and local costmap and tested for various values and changed the follow path plugin from **DWB** to **RPP**


## Contact Info 
 - Name: Chaitanya Ahire
 - Contact number: 7768857567
 - Email Address: ahirechaitanya4@gmail.com

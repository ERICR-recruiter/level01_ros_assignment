# Level 1: ROS2 Navigation Assignment - YOUR FULL NAME

## Overview

At ERIC Robotics, we’re big believers in building software with modularity. The nav2 stack reflects this perfectly with flexible, plugin-based framework, allowing you to pick and choose which pieces you need and run them independently. In this assignment, you’ll walk through the navigation workflow step by step—manually creating and calling actions—to bring an autonomous robot to life.

Here’s what to do:

We have shared some starter code for the 'Testbed-T1.0.0', a simple open-source robot developed by the team here at ERIC Robotics. Please note that there are some bugs intentionally left in the starter code that you will need to identify and fix. You also need to make a text file listing the bugs you were able to identify and how did you fix them and add that file in the root directory outside the navigation package. Your task is to develop a new ROS2 package called `testbed_navigation` to manage the navigation workflow for this robot.
However, rather than simply calling `nav2_bringup`, in this assignment you will manually build the required action components (i.e., using the map_server, amcl, planner plugins, and bt_ plugins) to run ros2 navigation, by working directly with the respective nav2 plugins.
i.e., In the `testbed_navigation` package, write individual launch files to load a map, perform localization, and navigate using the plugins provided by nav2.
Document your process so we can see how you tackled the task.
This assignment gives you hands-on experience with ROS2’s navigation plugins, while showcasing your ability to design modular and effective robotics solutions.

## Deadline & submissions

Four days (96 hrs) from the moment you accept the assignment.
All applicants should fork the repository for the assignment. To submit your code, after completion create a Pull Request (PR) back to the main branch. You can commit any number of times to your fork before your deadline.

## Repository Structure

```
ros_nav2_assignment/
├── testbed_description/
│   ├── launch/            # Launch the full base simulation
│   ├── meshes/
│   ├── rviz/              # RVIZ configuration files
│   └── urdf/              # URDF files for Testbed-T1.0.0
├── testbed_gazebo/
│   ├── worlds/            # Simulation world files
│   ├── launch/            # Launch files for Gazebo
│   └── models/            # Misc. Gazebo model files
├── testbed_bringup/
│   ├── launch/            # Launch file for bringing up the robot
│   └── maps/              # Predefined map of the test environment
├── testbed_navigation/    # NEW: navigation package (launch, config, README, docs)
├── BUGS.txt               # NEW: bugs found in the starter code and their fixes
├── help.md                # Guidelines and FAQs
└── README.md              # Instructions for the assignment
```

## Assignment Objective

Your goals are to:

- Learn how to configure and use ROS2 nav2 plugins in independent files.
- Set up manual map loading and localization for the given simulation environment.
- Implement the required navigation plugins to handle robot navigation in the `testbed_navigation` package. Only basic navigational functionality is expected in this assignment, so choose your plugins accordingly.

## Requirements

To get started, you’ll need:

- ROS2 Humble installed. (Install from Humble Installation) (You will need Ubuntu 22.04/Windows 10 for this. More in the help section.)
- Gazebo simulator (version 11.10.2 is compatible with ROS2 Humble) (Install from Gazebo Installation) and Rviz simulator.
- Basic to intermediate knowledge of ROS2 navigation concepts.
- Familiarity with creating and managing ROS2 packages, actions, and parameter files.
- The reference documentation for the nav2 stack is going to be your best friend for this assignment: Nav2 Documentation.

## Instructions

### 1. Setting Up the Repository

Create your workspace: `mkdir -p ~/assignment_ws/src`

Fork this repository to your GitHub account, then clone your fork:

```bash
cd ~/assignment_ws/src
git clone <your-fork-url>
```

Build the workspace:

```bash
cd ~/assignment_ws/
colcon build
source install/setup.bash
```

### 2. Launching the Simulation Environment

Start the full simulation using:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

This brings up the testbed environment in Gazebo and Rviz.

### 3. Creating the testbed_navigation Package

In your workspace, create a new package:

```bash
ros2 pkg create testbed_navigation --build-type ament_cmake
```

Set up the necessary directories for parameters, launch files, and scripts. Write proper build commands in `CMakeLists.txt` for your navigation package.

### 4. Map Loading

- Use the map provided in `testbed_bringup/maps/testbed_world.yaml`.
- Write actions in the launch file `testbed_navigation/launch/map_loader.launch.py` to load the map using the map_server plugin.
- Test and confirm that the map is loaded correctly in Rviz.

### 5. Localization

Implement localization with the AMCL plugin:

- Write a parameter file for AMCL in `testbed_navigation/config/amcl_params.yaml`.
- Create actions in the launch file `testbed_navigation/launch/localization.launch.py` to run AMCL.
- Verify that the robot can localize itself in the simulated environment using Rviz.

### 6. Navigation

Set up navigation using nav2 plugins:

- Configure parameter files for the global and local planners, behaviour tree plugins and any other nav2 plugin you want to use, like 'collision_monitor' or 'velocity_smoother', in `testbed_navigation/config/nav2_params.yaml`.
- Write actions in the launch file `testbed_navigation/launch/navigation.launch.py` to bring up the navigation workflow.
- Test the navigation setup by sending goals to the robot and observing its behavior.

### 7. Deliverables

Submit your completed `testbed_navigation` package with:

- Parameter files for map loading, localization, and navigation.
- Launch files for each component.
- A README.md describing your approach and any challenges you faced.
- Provide a short video or screenshots showing your robot performing localization and navigation.

### 8. Evaluation Criteria

We’ll be looking for:

- A functional manual navigation setup.
- Clear, well-structured parameter files and launch files.
- A modular, well-documented implementation.
- Successful localization and navigation in the simulation.

## Notes

- You’re welcome to modify the robot description or simulation setup to better suit your implementation.
- Thorough testing is encouraged to ensure everything works as expected.
- If you have questions, check out the help section and don’t hesitate to reach out to us.
- Lastly, we encourage you to share your code for review—even if it’s still a work in progress.

We’re excited to see how you approach this task. Good luck, and happy coding! :)

---

## Candidate Submission

### What was done

- Fixed the bugs left in the starter code. The full list, with file names and fixes, is in [`BUGS.txt`](BUGS.txt) in the repository root.
- Created the `testbed_navigation` package with one launch file per stage (map loading, localization, navigation) and separate parameter files. Approach, frames, challenges and screenshots are in [`testbed_navigation/README.md`](testbed_navigation/README.md).

### Bugs fixed in the starter code

1. `testbed_description/CMakeLists.txt`: `ament_package` was missing its parentheses, which broke the workspace build.
2. `testbed_bringup/maps/testbed_world.yaml`: wrong map image path.
3. `testbed_description/urdf/testbed.gazebo`: stray `>` made the XML malformed.
4. `testbed_description/urdf/testbed.gazebo`: lidar max range raised from 1.5 m to 12 m so localization works on this map.
5. `testbed_description/launch/robot_description.launch.py`: `use_sim_time` was not set for `robot_state_publisher`.
6. `testbed_bringup/CMakeLists.txt`: the `maps` folder was not installed.

### How to run

```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash

ros2 launch testbed_bringup testbed_full_bringup.launch.py        # terminal 1: simulation
ros2 launch testbed_navigation map_loader.launch.py               # terminal 2: map server
ros2 launch testbed_navigation localization.launch.py             # terminal 3: AMCL
ros2 launch testbed_navigation navigation.launch.py               # terminal 4: Nav2
```

In RViz: set Fixed Frame to `map` (it appears once AMCL is running), add the Map display on `/map` with Durability Policy `Transient Local`, use 2D Pose Estimate if the scan does not line up with the map, then send a 2D Goal Pose.

### Demo

Video: <ADD LINK HERE>

## Contact Info

Name: YOUR FULL NAME
Contact number: YOUR CONTACT NUMBER
Email Address: YOUR EMAIL ADDRESS

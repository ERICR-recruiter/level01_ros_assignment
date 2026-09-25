# Level 1: ROS2 Navigation Assignment - Gurvesh Singh

> ## Submission notes
>
> - **The navigation package is [`testbed_navigation/`](testbed_navigation/).**
>   Its [README](testbed_navigation/README.md) covers the design, the plugin
>   choices and the problems I ran into.
> - **The bug list the brief asks for is [`BUGS.md`](BUGS.md)** — seven defects
>   in the starter code, with the symptom and the fix for each.
> - **I ran this on Ubuntu 24.04 / ROS 2 Jazzy / Gazebo Harmonic**, not
>   22.04 / Humble / Gazebo Classic. Gazebo Classic is end-of-life and is not
>   available on 24.04. The port is written up in
>   [`MIGRATION.md`](MIGRATION.md).
>
> Quick start, two terminals:
>
> ```bash
> ros2 launch testbed_bringup testbed_full_bringup.launch.py rviz:=false
> ros2 launch testbed_navigation navigation.launch.py
> ```
>
> Then use **2D Goal Pose** in RViz, or
> `ros2 run testbed_navigation send_goal.py -5.0 -5.0`.

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
├── testbed_navigation/    # ── submitted ──
│   ├── config/            # map_server, AMCL and nav2 parameter files
│   ├── launch/            # map_loader, localization, navigation
│   ├── rviz/              # Navigation view, map-framed
│   ├── scripts/           # send_goal.py, NavigateToPose from the CLI
│   └── README.md          # Approach, design decisions, challenges
├── BUGS.md                # ── submitted ── bugs found in the starter code
├── MIGRATION.md           # ── submitted ── Humble/Classic -> Jazzy/Harmonic port
├── help.md                # Guidelines and FAQs
└── README.md              # Instructions for the assignment
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

> **What this submission was built and tested against:** Ubuntu 24.04, ROS 2
> Jazzy, Gazebo Harmonic 8.11 (`ros_gz`), Nav2 1.3.12. See
> [MIGRATION.md](MIGRATION.md) for what had to change and why.

## Instructions

### 1. Setting Up the Repository
1. Create your workspace:
    ```bash
    mkdir -p ~/assignment_ws/src
    ```
2. Fork this repository to your GitHub account, then clone your fork:
   ```bash
   cd ~/assignment_ws/src
   git clone <your-fork-url>
   ```
2. Build the workspace:
   ```bash
   cd ~/assignment_ws/
   colcon build
   source install/setup.bash
   ```

### 2. Launching the Simulation Environment
1. Start the full simulation using:
   ```bash
   ros2 launch testbed_bringup testbed_full_bringup.launch.py
   ```
   This brings up the testbed environment in Gazebo and Rviz.

### 3. Creating the `testbed_navigation` Package
1. In your workspace, create a new package:
   ```bash
   ros2 pkg create testbed_navigation --build-type ament_cmake
   ```
2. Set up the necessary directories for parameters, launch files, and scripts.
3. Write proper build commands in CMakeLists.txt for your navigation package.

### 4. Map Loading
1. Use the map provided in `testbed_bringup/maps/testbed_world.yaml`.
2. Write actions in the launch file `testbed_navigation/launch/map_loader.launch.py` to load the map using the `map_server` plugin.
3. Test and confirm that the map is loaded correctly in Rviz.

### 5. Localization
1. Implement localization with the AMCL plugin:
   - Write a parameter file for AMCL in `testbed_navigation/config/amcl_params.yaml`.
   - Create actions in the launch file `testbed_navigation/launch/localization.launch.py` to run AMCL.
   - Verify that the robot can localize itself in the simulated environment using Rviz.

### 6. Navigation
1. Set up navigation using `nav2` plugins:
   - Configure parameter files for the global and local planners, behaviour tree plugins and any other nav2 plugin you want to use, like 'collision_monitor' or 'velocity_smoother', in `testbed_navigation/config/nav2_params.yaml`.
   - Write actions in the launch file `testbed_navigation/launch/navigation.launch.py` to bring up the navigation workflow.
2. Test the navigation setup by sending goals to the robot and observing its behavior.

### 7. Deliverables
1. Submit your completed `testbed_navigation` package with:
   - Parameter files for map loading, localization, and navigation.
   - Launch files for each component.
   - A `README.md` describing your approach and any challenges you faced.
2. Provide a short video or screenshots showing your robot performing localization and navigation.

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
---

We’re excited to see how you approach this task. Good luck, and happy coding! :)

## Contact Info 
 - Name: Gurvesh Singh
 - Contact number: <add before submitting>
 - Email Address: gurveshsingh14@gmail.com

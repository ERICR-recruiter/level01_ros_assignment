# Level 1: ROS2 Navigation Assignment - Swarnava Roy

## Overview
At ERIC Robotics, we’re big believers in building software with modularity. The nav2 stack reflects this perfectly with flexible, plugin-based framework, allowing you to pick and choose which pieces you need and run them independently. In this assignment, you’ll walk through the navigation workflow step by step—manually creating and calling actions—to bring an autonomous robot to life.

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
```

## Assignment Objective
Your goals are to:
1. Learn how to configure and use ROS2 `nav2` plugins in independent files.
2. Set up manual map loading and localization for the given simulation environment.
3. Implement the required navigation plugins to handle robot navigation in the `testbed_navigation` package. Only basic navigational functionality is expected in this assignment, so choose your plugins accordingly.


### 7. Deliverables
1. Submit your completed `testbed_navigation` package with:
   - Parameter files for map loading, localization, and navigation.
   - Launch files for each component.
   - A `README.md` describing your approach and any challenges you faced.
2. Provide a short video or screenshots showing your robot performing localization and navigation.


We’re excited to see how you approach this task. Good luck, and happy coding! :)

## Contact Info 
 - Name: Swarnava Roy
 - Contact number: 9830057695
 - Email Address: royswarnava2006@gmail.com

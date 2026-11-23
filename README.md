# ros_assignment_ericr


# ROS 2 Navigation Assignment – Testbed T1.0.0

This repository contains my implementation and investigation of the ROS 2 Navigation Assignment provided by ERIC Robotics.

The objective is to understand the robot simulation environment, investigate the provided ROS 2 packages, identify and resolve starter-code issues, and develop a modular navigation system using individual Nav2 components.

## 🎥 Project Demonstration

**Watch the robot simulation and navigation demonstration:**

[▶ Watch Project Demonstration Video](testbed_media/Screencast%20from%2011-23-2026%2004_34_01%20PM.mp4)

The demonstration video is available in the `testbed_media` directory.

## Development Environment

| Component | Version |
|---|---|
| Operating System | Ubuntu 22.04 |
| ROS 2 | Humble|
| Build System | Colcon |
| Robot Simulator | Gazebo |
| Visualization | RViz2 |
| Programming | Python |

## Repository Structure

```text
ros_nav2_assignment_ws/
├── documentation/
│   └── tf_tree/
├── src/
│   ├── testbed_bringup/
│   ├── testbed_controller/
│   ├── testbed_description/
│   └── testbed_gazebo/
├── BUGS_AND_DEBUGGING.md
├── README.md
└── .gitignore
```

## Work Completed
- Investigated and corrected issues in the starter packages.
- Configured robot description and Gazebo simulation.
- Implemented map loading and AMCL localization.
- Configured Nav2 planner, controller, behavior tree, and supporting servers.
- Integrated navigation launch files and parameter configurations.
- Tested robot localization and navigation in simulation.
- Documented debugging observations and implementation details.

## Deliverables
- ROS 2 navigation package.
- Configuration and launch files.
- Documentation and debugging notes.
- Simulation demonstration video.

---

## 🔍 Debugging and Development Notes

During development, several issues were investigated and addressed across different ROS 2 components.

Some of the debugging areas included:

- CMake and XML syntax corrections.
- URDF/Xacro parameter handling.
- TF timestamp warnings and duplicate transform publishers.
- RViz map subscription and QoS durability configuration.
- Circular package dependencies during Colcon builds.
- Map server lifecycle transition failures.
- Nav2 controller and planner parameter tuning.
- Robot rotation and goal-reaching behaviour.

Detailed debugging observations, errors, and corrective actions are documented here:

[View BUGS_AND_DEBUGGING.md](testbed_media/BUGS_AND_DEBUGGING.md)

---

## Contact Info
---------
- Name: Kadavergu Saivenkat
- Contact number: 9398704613
- Email Address: saivenkatkadavergu@gmail.com

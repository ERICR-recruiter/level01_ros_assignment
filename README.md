# 🤖 ERIC Robotics: Navigation Simulation Assignment

![ROS2](https://img.shields.io/badge/ros2-Humble-blue.svg) ![Gazebo](https://img.shields.io/badge/gazebo-Ignition-orange.svg)

**Submitted by:** Visruth K  
📧 **Email:** visruthkelambeth@outlook.com  
📱 **Phone:** +91 7603912785  

> ⚠️ **Note:** Please see the `journal.txt` file in this repository for the video demonstration link and the detailed breakdown of the fixed bugs.

---

## Instructions to get started

Follow these steps to build the packages and start the simulation environment.

```bash
# Navigate to the workspace source directory
cd ~/assignment_ws/src

# Clone the repository
git clone https://github.com/inruth/inruths_fork

# Return to the workspace root
cd ~/assignment_ws

#initialize your main ros2 installation

#run the build commands
colcon build
source install/setup.bash

#run the simulation
ros2 launch testbed_bringup master.launch.py

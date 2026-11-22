# Level 1: ROS2 Navigation Assignment - Shashank

## Overview
At ERIC Robotics, we're big believers in building software with modularity. The nav2 stack reflects this perfectly with flexible, plugin-based framework, allowing you to pick and choose which pieces you need and run them independently. In this assignment, you'll walk through the navigation workflow step by step—manually creating and calling actions—to bring an autonomous robot to life.

For full implementation details, architecture notes, and launch instructions for the completed `testbed_navigation` package, see [`testbed_navigation/README.md`](testbed_navigation/README.md).
For the list of starter-code bugs identified and fixed, see [`bugs_and_fixes.txt`](bugs_and_fixes.txt).

## Quick Start

```bash
# 1. Build and source workspace
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash

# 2. Recommended DDS for reliable Nav2 action calls (see help.md)
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# 3. Terminal 1: Launch Gazebo + Robot + RViz2
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# 4. Terminal 2: Load the map
ros2 launch testbed_navigation map_loader.launch.py

# 5. Terminal 3: Start AMCL localization
ros2 launch testbed_navigation localization.launch.py

# 6. Terminal 4: Start the manual Nav2 navigation stack
ros2 launch testbed_navigation navigation.launch.py
```

## Contact Info
- Name: Shashank Patil
- Contact number: 9449913019
- Email Address: shashankrpatil077@gmail.com

#!/bin/bash
# Start the ROS 2 environment
source /opt/ros/humble/setup.bash

# Source the assignment workspace
source ~/assignment/install/setup.bash

echo "Starting AMR simulation, localization and navigation..."

ros2 launch testbed_navigation full_navigation_bringup.launch.py

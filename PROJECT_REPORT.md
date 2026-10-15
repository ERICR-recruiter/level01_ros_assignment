# ERIC Robotics ROS Intern Assignment
## Testbed-T1.0.0 ROS 2 Navigation Project

**Candidate:** Adithya P. S.
**Environment:** ROS 2 Humble in Docker, Gazebo, Nav2

## 1. Objective
Develop a separate ROS 2 navigation package, identify starter-code issues, and document the implementation and testing process.

## 2. Implementation
The testbed_navigation package contains separate launch files for map loading, AMCL localization, and Nav2 navigation, plus a Nav2 parameter configuration file. The package is intended to configure navigation components directly rather than relying on the standard nav2_bringup navigation launch.

## 3. Documented Issues
See bugs.txt for the recorded changes involving the map image path, map installation, simulation time, Gazebo sensor XML, AMCL parameters, costmap configuration, and LiDAR range improvement.

## 4. Verification Results
- Workspace build: passed; four packages finished.
- Gazebo simulation: started, with robot-related nodes visible.
- Map server: reached the active lifecycle state.
- Map topic: /map was available.
- AMCL: reached the active lifecycle state.
- AMCL pose output: not confirmed in the latest test.
- Complete navigation goal: requires further verification.

## 5. Build Instructions
Run inside the ROS 2 Humble Docker container from the workspace root:



## 6. Remaining Tests
1. Start the simulation and verify the robot is present.
2. Confirm the map server publishes /map.
3. Set a valid initial pose for AMCL.
4. Verify /amcl_pose and required TF transforms.
5. Start Nav2 and verify its actions are available.
6. Send a navigation goal and record whether it succeeds.

## 7. Conclusion
The navigation package and documentation have been prepared, and the recorded build and map-server checks passed. Localization output and a complete navigation-goal test remain unverified. The project should not be described as fully tested until those checks pass.

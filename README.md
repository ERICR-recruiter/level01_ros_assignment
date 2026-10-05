# Level 1: ROS2 Navigation Assignment- Shiva Sai Vangala

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
 - Name: Shiva Sai Vangala
 - Contact number:+61416652923
   Whatsapp:+919346432923
 - Email Address: saishiva791@gmail.com

# Implementation

## Approach

I created a separate ROS2 package called `testbed_navigation` and configured the Nav2 components individually instead of using `nav2_bringup`.

The navigation system was divided into three stages:

1. Map loading
2. Localization
3. Navigation

This keeps each part modular and allows the components to be tested independently.

## Map Loading

The provided map is loaded using `nav2_map_server`.

Launch command:

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

The launch file starts the map server together with a lifecycle manager. The supplied `testbed_world.yaml` map is loaded and published on `/map`.

## Localization

Localization is implemented using AMCL.

Configuration file:

```text
testbed_navigation/config/amcl_params.yaml
```

Launch command:

```bash
ros2 launch testbed_navigation localization.launch.py
```

AMCL uses:

- `/map` as the global map
- `/scan` for LiDAR measurements
- `/odom` for odometry
- `base_footprint` as the robot base frame

After setting the initial robot pose in RViz using **2D Pose Estimate**, AMCL successfully provides the `map -> odom` transform and tracks the robot position on the map.

## Navigation

Navigation parameters are configured in:

```text
testbed_navigation/config/nav2_params.yaml
```

The navigation launch file manually starts the required Nav2 components instead of calling `nav2_bringup`.

The following nodes are launched:

- `planner_server`
- `controller_server`
- `behavior_server`
- `bt_navigator`
- `nav2_lifecycle_manager`

Launch command:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

### Global Planner

The NavFn planner is used for global path planning:

```text
nav2_navfn_planner/NavfnPlanner
```

It generates a path from the robot's current position to the requested goal.

### Local Controller

The DWB local planner is used for path following:

```text
dwb_core::DWBLocalPlanner
```

The controller follows the generated path and publishes velocity commands on `/cmd_vel`.

### Costmaps

A global and local costmap are configured.

The global costmap uses:

- the saved map
- LiDAR obstacle information
- an inflation layer

The local costmap uses:

- a rolling window around the robot
- live `/scan` data
- an obstacle layer
- an inflation layer

## Behavior Tree

`bt_navigator` coordinates planning, path following and recovery actions.

The configured recovery behaviors include:

- spin
- backup
- wait

## LiDAR Tuning

The supplied simulated LiDAR initially had a maximum range of approximately 1.5 m.

During testing, the short range provided limited environmental information to AMCL, especially during turns and in larger open areas.

The simulated LiDAR maximum range was increased to 5.0 m.

The AMCL and Nav2 costmap parameters were also updated to match the new LiDAR range.

This improved localization stability during turns and provided better obstacle information for navigation.

## Testing

The following functionality was successfully tested:

- Robot spawned correctly in Gazebo
- Robot responded correctly to `/cmd_vel`
- LiDAR published valid `/scan` data
- Map loaded correctly in RViz
- AMCL localized the robot successfully
- `map -> odom` transform was generated
- Nav2 lifecycle nodes activated successfully
- Global and local costmaps operated correctly
- Navigation goals were accepted from RViz
- Global paths were generated
- Robot followed the planned path
- Robot successfully navigated through turns
- Robot reached the requested goal positions

## Screenshots

### AMCL Localization

![AMCL Localization](screenshots/localisation.png)

### Navigation Path

![Navigation Path](screenshots/navigationimage.png)

### Gazebo and RViz Navigation

![Gazebo and RViz](screenshots/gazebowithrviz.png)

### Navigation Goal Reached

![Navigation Goal Reached](screenshots/navigationreachedgoal.png)

## Challenges Faced

### CMake Build Error

The starter `testbed_description/CMakeLists.txt` contained:

```cmake
ament_package
```

instead of:

```cmake
ament_package()
```

This caused the initial workspace build to fail. Adding the parentheses fixed the CMake error.

### Map Directory Not Installed

The `maps` directory was not included in the installation configuration of `testbed_bringup`.

The CMake installation configuration was updated so the map files are available from the installed package.

### Incorrect Map Image Path

The supplied map YAML referenced:

```text
wrong_path_testbed_world.pgm
```

The path was corrected to:

```text
testbed_world.pgm
```

After this fix, `nav2_map_server` successfully loaded the supplied map.

### Simulation Time Synchronization

`robot_state_publisher` initially did not use simulation time while Gazebo was running with simulation time.

`use_sim_time` was enabled for `robot_state_publisher` so TF timestamps were consistent with the simulation.

### Costmap Parameter Type

During initial navigation testing, the local costmap failed because `width` and `height` were provided as floating-point values.

They were changed to integer values expected by Nav2 Humble.

After this correction, all navigation lifecycle nodes configured and activated successfully.

## Running the Complete System

Build and source the workspace:

```bash
cd ~/assignment_ws
colcon build
source install/setup.bash
```

### Terminal 1 - Simulation

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### Terminal 2 - Map Server

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

### Terminal 3 - Localization

```bash
ros2 launch testbed_navigation localization.launch.py
```

Set the initial robot pose using **2D Pose Estimate** in RViz.

### Terminal 4 - Navigation

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Navigation goals can then be sent using **2D Goal Pose** in RViz.

## Result

The completed ROS2 navigation system successfully performs map loading, AMCL localization, global path planning, local path following and autonomous navigation in the supplied Gazebo environment.

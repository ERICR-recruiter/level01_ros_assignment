# Testbed Navigation Package (`testbed_navigation`)

This package provides a complete ROS 2 navigation and localization framework using Nav2 plugins for the testbed mobile robot in simulation.

**Project Video Folder:** https://drive.google.com/drive/folders/1WeGvvEcSqkzYXr9VQpYGvBeTSkNc2lHm

## 1. Overview & Navigation Approach

The navigation workflow is built around the standard Nav2 architecture, divided into modular launch and configuration files:

* **Map Server (`map_loader.launch.py`):** Loads the occupancy grid map (`testbed_world.yaml`) and manages map lifecycle transitions.
* **Localization (`amcl.launch.py`):** Uses Adaptive Monte Carlo Localization (`amcl`) combined with sensor data to estimate the robot's pose on the map. Initial pose configurations are defined directly in `amcl_params.yaml`.
* **Navigation Stack (`navigation.launch.py`):** Spawns and manages the core Nav2 servers:
  * **Planner Server:** Utilizes `nav2_navfn_planner::NavfnPlanner` (Global Planner) to compute the global path.
  * **Controller Server:** Utilizes `dwb_core::DWBLocalPlanner` (Local Planner) along with custom progress and goal checkers to follow the path safely.
  * **Behavior Server:** Manages recovery behaviors (`spin`, `backup`, `wait`, `drive_on_heading`).
  * **BT Navigator:** Coordinates overall mission execution using Behavior Trees (`NavigateToPose` and `NavigateThroughPoses`).

## 2. Launch Files

The package includes three primary Python launch files located in `testbed_navigation/launch/`:

1. `map_loader.launch.py`: Brings up the `map_server` and its lifecycle manager.
2. `localization.launch.py`: Brings up `amcl` alongside the map loader for localization.
3. `navigation.launch.py`: Starts up the global planner, controller server, behavior server, and BT navigator lifecycle nodes.

## 3. Launch Order

Run each command in a separate terminal (source your workspace in each: `source install/setup.bash`).

1. **Bringup (Gazebo + robot):**
```bash
   ros2 launch testbed_bringup testbed_full_bringup.launch.py
```
2. **ROS–Gazebo bridge** (so topics like `/scan`, `/odom`, `/clock`, `/tf` flow between Gazebo and ROS 2):
```bash
   ros2 run ros_gz_bridge parameter_bridge <topic_mappings> 
   (ros2 run ros_gz_bridge parameter_bridge \
  '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock' \
  '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist' \
  '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry' \
  '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V' \
  '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan' \
  '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model' \
  '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU'
)
```
3. **Map_Loader:**
```bash
   ros2 launch testbed_navigation map_loader.launch.py (add map and change durability to Transient_Local)
  
```
5. **Localization:**
```bash
   ros2 launch testbed_navigation localization.launch.py
```

6. **Navigation:**
```bash
   ros2 launch testbed_navigation navigation.launch.py
```

## 4. Challenges Faced & Solutions

* **Initial Pose Desynchronization:**
  * *Challenge:* The robot often spawned with an unknown or incorrect initial pose, causing AMCL particle distribution to fail and RViz to display transformation errors.
  * *Solution:* Enabled `set_initial_pose: true` and explicitly configured the starting coordinates in the `amcl` parameter file to align with the Gazebo spawn point.

* **LiDAR Returning `inf` or `0` Values:**
  * *Challenge:* The simulated LiDAR scan was showing `inf` or `0` readings because the sensor's maximum range was too short for the environment.
  * *Solution:* Changed the LiDAR maximum range in `testbed.gazebo` from 1.5 to 12.


## 5. Deliverables & Testing

* Parameter files for map loading, localization (`amcl_params.yaml`), and navigation (`nav2_params.yaml`).
* Modular launch files for each system component.
* Verified localization and goal navigation in Gazebo and RViz.

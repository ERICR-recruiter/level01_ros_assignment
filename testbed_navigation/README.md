# testbed_navigation

Manual ROS 2 Nav2 navigation package for **Testbed-T1.0.0** (ROS 2 Jazzy + Gazebo Sim).

## Approach

Instead of using `nav2_bringup`, each navigation component is launched and lifecycle-managed explicitly:

1. **Map Loading (`launch/map_loader.launch.py`)**:
   - Launches `nav2_map_server` (`map_server`) with `testbed_bringup/maps/testbed_world.yaml` and a dedicated `nav2_lifecycle_manager` (`lifecycle_manager_map`).
2. **Localization (`launch/localization.launch.py`, `config/amcl_params.yaml`)**:
   - Launches `nav2_amcl` (`amcl`) configured for `DifferentialMotionModel`, `base_footprint` / `odom` / `map` frames, `/scan` topic, and initial pose `(0.0, 5.0, 0.0)` matching the robot's spawn pose.
   - Managed by `lifecycle_manager_localization`.
3. **Navigation (`launch/navigation.launch.py`, `config/nav2_params.yaml`)**:
   - Manually launches `controller_server` (`RegulatedPurePursuitController`), `smoother_server` (`SimpleSmoother`), `planner_server` (`NavfnPlanner`), `behavior_server` (`Spin`, `BackUp`, `DriveOnHeading`, `Wait`), `bt_navigator`, and `velocity_smoother` (smoothing `cmd_vel_nav` -> `cmd_vel`).
   - Managed by `lifecycle_manager_navigation`.
4. **Goal Testing (`scripts/send_goal.py`)**:
   - Python `NavigateToPose` action client for sending navigation goals from the command line.

## Usage

```bash
# Terminal 1: Start simulation & RViz
source /opt/ros/jazzy/setup.bash
source ~/assignment_ws/install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# Terminal 2: Load the map
ros2 launch testbed_navigation map_loader.launch.py

# Terminal 3: Start AMCL localization
ros2 launch testbed_navigation localization.launch.py

# Terminal 4: Start manual Nav2 navigation stack
ros2 launch testbed_navigation navigation.launch.py

# Terminal 5 (optional): Send a navigation goal via CLI
ros2 run testbed_navigation send_goal.py --x 2.0 --y 2.0 --yaw 0.0
```

## Challenges Faced

- **Starter Code Bugs**: Missing parentheses in `testbed_description/CMakeLists.txt` (`ament_package`), missing `install(DIRECTORY ...)` entries for `maps` and `models`, and an invalid PGM image path in `testbed_world.yaml`.
- **Gazebo Classic to Gazebo Sim Migration**: On ROS 2 Jazzy, `gazebo_ros` is replaced by `ros_gz_sim` + `ros_gz_bridge` + `gz_ros2_control`. Bridging `/clock`, `/scan`, and `/imu` and adding `gz-sim-sensors-system` to the world file were required for sensor data and `use_sim_time` to work.
- **Lidar Range**: Increasing the lidar max range from 1.5 m to 12.0 m improved AMCL particle convergence and costmap clearing in the ~20 m playground environment.

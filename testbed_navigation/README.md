# testbed_navigation

Modular ROS 2 Humble navigation package for **Testbed-T1.0.0**, built using standalone Nav2 servers and `nav2_lifecycle_manager` nodes without `nav2_bringup`.

## Structure & Workflow
- **`launch/map_loader.launch.py` (`config/map_server_params.yaml`)**: Launches `nav2_map_server` to publish `testbed_world.yaml` on `/map` and activates it via `lifecycle_manager_map`.
- **`launch/localization.launch.py` (`config/amcl_params.yaml`)**: Includes `map_loader.launch.py` and runs `nav2_amcl` (`DifferentialMotionModel`, likelihood-field laser model) to publish the `map -> odom` transform.
- **`launch/navigation.launch.py` (`config/nav2_params.yaml`)**: Includes `localization.launch.py` and launches `planner_server` (`NavfnPlanner`), `controller_server` (`DWBLocalPlanner`), `behavior_server` (`Spin`, `BackUp`, `DriveOnHeading`, `Wait`), and `bt_navigator`.

## How to Run
```bash
# Terminal 1: Simulation & RViz
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# Terminal 2: Modular Nav2 Stack
ros2 launch testbed_navigation navigation.launch.py
```

## Challenges & Fixes
- **Sim Clock Sync:** `robot_state_publisher` ran on system wall time while Gazebo published `/clock`, causing TF extrapolation errors. Passing `use_sim_time: True` across all nodes resolved TF lookups.
- **Starter Bugs:** Fixed the URDF syntax error, increased LiDAR max range (`1.5m` to `10.0m`), and corrected the map `.pgm` filename in `testbed_world.yaml` (full list in `../bugs_fixed.txt`).
- **Doorway Clearance:** Tuned `robot_radius: 0.22` and `inflation_radius: 0.45` in both costmaps so the robot navigates cleanly through narrow doorways.
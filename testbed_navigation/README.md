# testbed_navigation

ROS 2 package providing modular autonomous navigation for the ERIC Robotics Testbed-T1.0.0 mobile robot.

## Architectural Design

To adhere strictly to ERIC Robotics assignment guidelines, this package does **not** rely on `nav2_bringup`. Instead, all Nav2 components are manually configured, instantiated, and managed through discrete ROS 2 launch actions and explicit lifecycle transitions.

### Three Modular Launch Files

1. **`map_loader.launch.py`**
   - Instantiates `nav2_map_server::map_server` and `nav2_lifecycle_manager::lifecycle_manager`.
   - Reads the map from `testbed_bringup/maps/testbed_world.yaml`.
   - Transitions `map_server` to `active [3]` and publishes `/map` (`nav_msgs/msg/OccupancyGrid`).
   - Command:
     ```bash
     ros2 launch testbed_navigation map_loader.launch.py
     ```

2. **`localization.launch.py`**
   - Instantiates `nav2_amcl::amcl` configured via `config/amcl_params.yaml`.
   - Uses `nav2_amcl::DifferentialMotionModel` for kinematics.
   - Publishes `/amcl_pose` and broadcasts the global `map` -> `odom` TF transform.
   - Pre-seeds initial pose at (x=0.0, y=5.0, yaw=0.0), matching the Gazebo spawn coordinates.
   - Command:
     ```bash
     ros2 launch testbed_navigation localization.launch.py
     ```

3. **`navigation.launch.py`**
   - Manually instantiates the core Nav2 servers:
     - `controller_server` with `dwb_core::DWBLocalPlanner` and local costmap.
     - `planner_server` with `nav2_navfn_planner/NavfnPlanner` and global costmap.
     - `behavior_server` with `Spin`, `BackUp`, `DriveOnHeading`, and `Wait` behaviors.
     - `bt_navigator` managing behavior tree execution.
     - `lifecycle_manager_navigation` managing the lifecycle transitions for all 4 servers.
   - Command:
     ```bash
     ros2 launch testbed_navigation navigation.launch.py
     ```

4. **`testbed_navigation.launch.py` (Unified Parent)**
   - Convenience launch file that composes all three subsystems for rapid execution and demonstration.
   - Command:
     ```bash
     ros2 launch testbed_navigation testbed_navigation.launch.py
     ```

## Configuration Files

- `config/amcl_params.yaml`: Motion model noise parameters, particle filter bounds (500–2000), beam likelihood field model, frame IDs (`map`, `odom`, `base_footprint`), and initial pose coordinates.
- `config/nav2_params.yaml`: Controller parameters (velocity/acceleration limits, critics, goal tolerances), Navfn global planner tolerance, costmap layers (static, obstacle, inflation), behavior plugins, and behavior tree navigators.
- `config/waypoints.yaml`: Semantic room definitions, map coordinates (x, y, yaw), and natural language alias mappings for high-level goal commanding.

## Semantic Navigation CLI (`move_to`)

The package includes a semantic command tool allowing users to command the robot by room name or natural language phrase instead of manual coordinates:

```bash
# Display all configured rooms and aliases
ros2 run testbed_navigation move_to --list

# Navigate to rooms by name or natural language
ros2 run testbed_navigation move_to living_room
ros2 run testbed_navigation move_to "go to bathroom"
ros2 run testbed_navigation move_to home
```

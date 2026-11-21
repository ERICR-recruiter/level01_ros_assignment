# testbed_navigation

`testbed_navigation` provides modular, standalone ROS 2 Nav2 navigation workflows for the ERIC Robotics **Testbed-T1.0.0** differential drive robot.

Instead of monolithic wrappers such as `nav2_bringup`, this package manually launches and lifecycle-manages individual Nav2 plugin nodes (`map_server`, `amcl`, `controller_server`, `planner_server`, `behavior_server`, `bt_navigator`, `waypoint_follower`, `velocity_smoother`) with tailored configurations.

---

## 1. Selected Plugins & Rationale for Testbed-T1.0.0

| Component | Selected Plugin / Node | Rationale for Testbed Robot |
| :--- | :--- | :--- |
| **Global Planner** | `nav2_navfn_planner/NavfnPlanner` | Testbed-T1.0.0 is a 2D ground mobile robot operating in flat, mapped indoor spaces. NavFn computes optimal, collision-free global Dijkstra/A* paths on a 2D occupancy grid efficiently without unnecessary kinematic complexity. |
| **Local Controller** | `dwb_core::DWBLocalPlanner` | DWB provides fine-grained trajectory rollouts specifically designed for non-holonomic differential drive kinematics ($v_y = 0, \dot{\theta} \neq 0$). Its critic-based architecture (`RotateToGoal`, `PathAlign`, `GoalDist`, `BaseObstacle`) handles in-place rotations and obstacle avoidance accurately. |
| **Costmaps** | `nav2_costmap_2d::ObstacleLayer`, `InflationLayer`, `StaticLayer` | Obstacle marking and raytracing are tuned to match the actual LiDAR sensor specs ($[0.10\,\text{m}, 1.50\,\text{m}]$). Robot circular radius is set to $0.25\,\text{m}$ (bounding wheel separation of $0.35\,\text{m}$), and inflation radius is set to $0.45\,\text{m}$ to maintain safe wall clearance. |
| **Recovery Behaviors** | `nav2_behaviors` (`Spin`, `BackUp`, `DriveOnHeading`, `Wait`) | Since Testbed-T1.0.0 is differential-drive, it can rotate in place (`Spin`) and reverse (`BackUp`) safely if trapped without violating kinematic limits. |
| **Velocity Smoother** | `nav2_velocity_smoother` | Smooths velocity commands from the controller before delivering them to `/cmd_vel` on Gazebo's diff-drive plugin, eliminating abrupt accelerations and wheel slip. |
| **BT Navigator** | `nav2_bt_navigator` | Utilizes the official ROS 2 Humble behavior tree `navigate_to_pose_w_replanning_and_recovery.xml` with complete built-in Humble plugin libraries, enabling 1 Hz replanning, recovery cascades, and goal tracking. |

---

## 2. Directory Structure

```
testbed_navigation/
├── CMakeLists.txt
├── package.xml
├── README.md
├── config/
│   ├── amcl_params.yaml          # AMCL localization parameters
│   ├── map_server_params.yaml    # Map server parameters
│   └── nav2_params.yaml          # Complete Nav2 stack parameters
└── launch/
    ├── map_loader.launch.py      # Independent map loading
    ├── localization.launch.py    # Map loader + AMCL localization
    └── navigation.launch.py      # Nav2 servers + BT navigator + lifecycle
```

---

## 3. Usage & Execution Instructions

Ensure the ROS 2 Humble workspace is built and sourced:
```bash
cd ~/assignment_ws
colcon build
source install/setup.bash
```

### Stage 1: Launch Full Base Simulation & RViz
```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### Stage 2: Map Loading (Independent)
```bash
ros2 launch testbed_navigation map_loader.launch.py use_sim_time:=true
```

### Stage 3: Localization (Map + AMCL)
```bash
ros2 launch testbed_navigation localization.launch.py use_sim_time:=true
```
In RViz, use **2D Pose Estimate** on topic `/initialpose` to verify particles and align pose.

### Stage 4: Navigation Workflow
```bash
ros2 launch testbed_navigation navigation.launch.py use_sim_time:=true
```
In RViz, click **2D Goal Pose** (`nav2_rviz_plugins/GoalTool`) to dispatch navigation action goals to `/navigate_to_pose`.

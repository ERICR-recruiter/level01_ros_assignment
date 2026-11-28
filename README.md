# Level 1: ROS 2 Navigation Assignment - Achal

## Project Overview

This repository contains the completed, repaired, and modularized **ERIC Robotics Level 1 ROS 2 Navigation Assignment** for the **Testbed-T1.0.0** differential-drive mobile robot, targeting **Ubuntu 22.04**, **ROS 2 Humble**, **Gazebo Classic 11**, and **Nav2**.

In accordance with the assignment specification, navigation is built **without** calling `nav2_bringup`. Instead, the `testbed_navigation` package configures and launches the individual Nav2 servers, plugins, and lifecycle managers independently across dedicated parameter files and modular launch files:

1. **Map Loading**: `map_server` + `lifecycle_manager_map` (`map_loader.launch.py` + `config/map_server_params.yaml`)
2. **Localization**: `amcl` + `lifecycle_manager_localization` (`localization.launch.py` + `config/amcl_params.yaml`)
3. **Autonomous Navigation**: `controller_server`, `smoother_server`, `planner_server`, `behavior_server`, `bt_navigator`, and `lifecycle_manager_navigation` (`navigation.launch.py` + `config/nav2_params.yaml`)
4. **Staged Convenience Bringup**: `bringup_navigation.launch.py` (launches the three modular stacks and RViz2 in a timed sequence to prevent lifecycle race conditions)

---

## System Architecture

### Package Layout

```text
level01_ros_assignment/
├── README.md                                 # Project documentation & assignment overview
├── BUGS_FIXED.md                             # Detailed bug audit & root-cause report (Markdown)
├── BUGS_FIXED.txt                            # Plain-text bug-fix report (root directory requirement)
├── TEST_REPORT.md                            # Static validation results & runtime test checklist
├── RUN_INSTRUCTIONS.md                       # Copy-pasteable terminal execution guide
├── help.md                                   # Original assignment FAQs
├── testbed_description/                      # Robot URDF/Xacro, STL meshes, Gazebo plugins, RViz configs
├── testbed_gazebo/                           # Gazebo Classic 11 worlds, models, and spawn launch files
├── testbed_bringup/                          # Full simulation bringup and predefined testbed_world map
└── testbed_navigation/                       # Modular Nav2 stack (map, AMCL, navigation, RViz)
    ├── CMakeLists.txt
    ├── package.xml
    ├── README.md
    ├── config/
    │   ├── map_server_params.yaml
    │   ├── amcl_params.yaml
    │   └── nav2_params.yaml
    ├── launch/
    │   ├── map_loader.launch.py
    │   ├── localization.launch.py
    │   ├── navigation.launch.py
    │   └── bringup_navigation.launch.py
    └── rviz/
        └── nav2_view.rviz
```

### TF Tree & Key Topics

```text
map  ──(amcl)──►  odom  ──(libgazebo_ros_diff_drive)──►  base_footprint
                                                               │
                                                (robot_state_publisher)
                                                               ▼
                                                           base_link
                                               ┌───────────┬───┴───┬──────────┐
                                               ▼           ▼       ▼          ▼
                                         lidar_link_1  imu_link_1 casters  wheels*
                                         (*wheel TFs published by diff_drive plugin)
```

| Topic / Action | Type | Publisher / Server | Consumer |
| :--- | :--- | :--- | :--- |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo (`gzserver`) | All nodes (`use_sim_time: true`) |
| `/scan` | `sensor_msgs/msg/LaserScan` | `libgazebo_ros_ray_sensor.so` (`lidar_link_1`, 12 m) | AMCL, Local & Global Costmaps |
| `/odom` | `nav_msgs/msg/Odometry` | `libgazebo_ros_diff_drive.so` | AMCL, Controller, BT Navigator |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `controller_server`, `behavior_server` | `libgazebo_ros_diff_drive.so` |
| `/map` | `nav_msgs/msg/OccupancyGrid` | `map_server` (Transient Local) | AMCL, Global Costmap, RViz2 |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz2 (`2D Pose Estimate`) | AMCL |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz2 (`2D Goal Pose`) | `bt_navigator` |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | `bt_navigator` | RViz2 / CLI |

---

## Prerequisites & Dependencies

- **OS**: Ubuntu 22.04 LTS (Jammy Jellyfish)
- **ROS 2**: ROS 2 Humble Hawksbill (`ros-humble-desktop`)
- **Simulator**: Gazebo Classic 11 (`gazebo11`, `ros-humble-gazebo-ros-pkgs`)
- **Navigation**: Nav2 (`ros-humble-navigation2`, `ros-humble-nav2-bringup`)
- **Recommended RMW**: Cyclone DDS (`ros-humble-rmw-cyclonedds-cpp`) to avoid Fast DDS discovery timeouts with Nav2

### Installation Instructions

```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-rmw-cyclonedds-cpp \
  ros-humble-tf2-tools \
  python3-colcon-common-extensions
```

Configure Cyclone DDS in your shell (or append to `~/.bashrc`):

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

---

## Workspace Build Instructions

```bash
mkdir -p ~/assignment_test_ws/src
# Place or clone the completed level01_ros_assignment repository into ~/assignment_test_ws/src/
cd ~/assignment_test_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## Running the Simulation & Navigation Stack

### Verified Launch Procedure

The following modular procedure was successfully tested on Ubuntu 22.04,
ROS 2 Humble and Gazebo Classic 11.

Use separate terminals. Keep each launched process running.

**Terminal 1  Gazebo simulation**

```bash
source /usr/share/gazebo/setup.sh
source /opt/ros/humble/setup.bash
source ~/assignment_test_ws/install/setup.bash

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export GAZEBO_PLUGIN_PATH=/opt/ros/humble/lib:$GAZEBO_PLUGIN_PATH
export LD_LIBRARY_PATH=/opt/ros/humble/lib:$LD_LIBRARY_PATH

ros2 launch gazebo_ros gazebo.launch.py \
  world:=$(ros2 pkg prefix testbed_gazebo)/share/testbed_gazebo/worlds/testbed_playground.world

**Terminal 2  Robot description and TF**

source /opt/ros/humble/setup.bash
source ~/assignment_test_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 launch testbed_description robot_description.launch.py use_sim_time:=true

**Terminal 3  Spawn the robot**

source /opt/ros/humble/setup.bash
source ~/assignment_test_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 run gazebo_ros spawn_entity.py \
  -entity testbed \
  -topic robot_description \
  -x 0 -y 5 -z 0.01

**Terminal 4  Load the map**

source /opt/ros/humble/setup.bash
source ~/assignment_test_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 launch testbed_navigation map_loader.launch.py use_sim_time:=true


**Terminal 5  Start localization**

source /opt/ros/humble/setup.bash
source ~/assignment_test_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 launch testbed_navigation localization.launch.py use_sim_time:=true


**Terminal 6  Start Nav2**

source /opt/ros/humble/setup.bash
source ~/assignment_test_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 launch testbed_navigation navigation.launch.py use_sim_time:=true

**Terminal 7  Open RViz**

source /opt/ros/humble/setup.bash
source ~/assignment_test_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 run rviz2 rviz2 \
  -d "$(ros2 pkg prefix testbed_navigation)/share/testbed_navigation/rviz/nav2_view.rviz" \
  --ros-args -p use_sim_time:=true

Set the robot's initial pose using RViz's 2D Pose Estimate tool.
Then use 2D Goal Pose to send a navigation goal.



---

## Localization & Navigation Goal Testing

1. **Set Initial Pose in RViz2**:
   - Confirm `Fixed Frame` is `map` and the occupancy grid (`/map`) and red LiDAR points (`/scan`) are visible.
   - Click **2D Pose Estimate** in the RViz2 toolbar, click near `(0.0, 5.0)` (the robot's spawn point in the upper corridor), and drag along `+X` (yaw `0.0`).
   - Verify the green AMCL particle cloud (`/particlecloud`) clusters tightly around the robot and the red `/scan` points align cleanly with the black map walls.
2. **Send a Navigation Goal in RViz2**:
   - Click **2D Goal Pose** (publishes to `/goal_pose`), click a free location inside the map (for example, `(2.0, 2.0)` or `(-5.0, 5.0)`), and drag to set the target heading.
   - Observe the green global plan (`/plan`), blue local plan (`/local_plan`), costmap inflation, and robot motion in Gazebo and RViz2.
3. **Optional CLI Goal Test**:
   ```bash
   ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
     "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 2.0, z: 0.0}, orientation: {w: 1.0}}}}"
   ```

---

## Troubleshooting

- **Nav2 timeouts or dropped `/scan` messages**: Ensure `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` is exported in every terminal.
- **TF extrapolation errors**: Confirm every node is running with `use_sim_time:=true` and `/clock` is actively publishing (`ros2 topic hz /clock`).
- **Map not visible in RViz2**: Ensure the Map display QoS Durability Policy is set to **Transient Local** (already preconfigured in `testbed_navigation/rviz/nav2_view.rviz`).
- **Gazebo cannot find models**: Rebuild with `colcon build` and re-source `install/setup.bash` so `testbed_gazebo/models` is installed and appended to `GAZEBO_MODEL_PATH`.
- **Robot fails to spawn**: `testbed_full_bringup.launch.py` delays `spawn_testbed.launch.py` by 3 seconds and uses `-timeout 60`. If Gazebo takes longer on first launch (downloading sun/ground_plane), wait for Gazebo to finish loading and run `ros2 launch testbed_gazebo spawn_testbed.launch.py` manually.

## Known Limitations

- **Combined launch:** `testbed_full_bringup.launch.py` caused Gazebo server crashes on the tested machine. Use the verified modular launch procedure documented above.
- **Gazebo Classic:** The tested Gazebo Classic 11.10.2 installation displays an end-of-life warning.
- **Initial pose:** AMCL requires a valid initial pose before reliable localization. Set the initial pose using RViz's 2D Pose Estimate tool.
- **Simulation time:** ROS 2 nodes must use simulation time when operating with the Gazebo clock.
- **DDS middleware:** Cyclone DDS was used consistently across terminals during the successful runtime demonstration.

The modular Gazebo, localization, and Nav2 workflow was successfully tested on Ubuntu 22.04 with ROS 2 Humble. See `TEST_REPORT.md` for the runtime verification results.

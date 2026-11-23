# testbed_navigation

Hand-assembled Nav2 navigation for the **Testbed-T1.0.0** robot. Instead of calling
`nav2_bringup`, each part of the navigation workflow is started directly from its
Nav2 plugin/server, with its own launch file and parameter file:

| Step | Launch file | Parameter file | Nodes started |
|------|-------------|----------------|---------------|
| 1. Map loading  | `launch/map_loader.launch.py`   | `config/map_server_params.yaml` | `map_server`, `lifecycle_manager_map` |
| 2. Localization | `launch/localization.launch.py` | `config/amcl_params.yaml`       | `amcl`, `lifecycle_manager_localization` (+ step 1 unless `load_map:=false`) |
| 3. Navigation   | `launch/navigation.launch.py`   | `config/nav2_params.yaml`, `behavior_trees/navigate_to_pose_testbed.xml` | `planner_server`, `controller_server`, `behavior_server`, `bt_navigator`, `velocity_smoother`, `lifecycle_manager_navigation` |
| All-in-one      | `launch/testbed_navigation_bringup.launch.py` | – | Gazebo + robot, steps 1–3 and RViz |

```
testbed_navigation/
├── behavior_trees/navigate_to_pose_testbed.xml   # BT used by bt_navigator
├── config/
│   ├── map_server_params.yaml
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   ├── navigation.launch.py
│   └── testbed_navigation_bringup.launch.py
├── rviz/testbed_navigation.rviz                   # RViz layout with the Nav2 panel
├── scripts/send_goal.py                           # send goals / run a demo tour
├── CMakeLists.txt
└── package.xml
```

## Setup

```bash
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-rmw-cyclonedds-cpp
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp      # recommended in help.md

mkdir -p ~/assignment_ws/src && cd ~/assignment_ws/src
git clone <fork-url>
cd ~/assignment_ws && colcon build --symlink-install && source install/setup.bash
```

## Running it step by step

Each step runs in its own terminal (source the workspace and set
`RMW_IMPLEMENTATION` in every terminal).

```bash
# 0. Simulation: Gazebo + robot + RViz
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# 1. Map only: check in RViz (Fixed Frame = map, add Map display on /map)
ros2 launch testbed_navigation map_loader.launch.py

# 2. Localization: AMCL against the map that is already running
ros2 launch testbed_navigation localization.launch.py load_map:=false

# 3. Navigation servers
ros2 launch testbed_navigation navigation.launch.py
```

Or start everything at once (Gazebo, map, AMCL, Nav2 and a Nav2 RViz):

```bash
ros2 launch testbed_navigation testbed_navigation_bringup.launch.py
# headless: ... rviz:=false gui:=false
```

### Sending goals

* **RViz**: use the **Nav2 Goal** tool on the toolbar and click/drag on the map.
* **CLI, single goal** (x, y, yaw in the map frame):
  `ros2 run testbed_navigation send_goal.py 5.0 5.0 0.0`
* **Demo tour** through both doorways of the world:
  `ros2 run testbed_navigation send_goal.py --tour`
* **Raw action**:
  `ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 5.0, y: 5.0}, orientation: {w: 1.0}}}}"`

AMCL is started with the robot's spawn pose `(0.0, 5.0, 0°)` as its initial pose,
so no "2D Pose Estimate" is needed. If you move the robot in Gazebo, set the pose
again with RViz's **2D Pose Estimate**.

## Design and approach

### 1. Understand the robot before tuning Nav2
I first fixed the starter code (see `../bugs_identified_and_fixed.txt`) and measured
the robot from its meshes rather than trusting the URDF numbers:

* the drive-axle centre is at (-0.050, -0.038) in `base_link`, so I moved `base_footprint` there
  so the robot rotates about `base_footprint`
* chassis + wheels then span x ∈ [-0.176, 0.174], y ∈ [-0.203, 0.203] → footprint
  `[[0.18, 0.21], [0.18, -0.21], [-0.18, -0.21], [-0.18, 0.21]]`
* wheel separation 0.376 m and diameter 0.1 m for the diff-drive plugin
* lidar: 360°, 300 beams, 0.1–12 m on `/scan`

I also measured the map: the doorways between the rooms are **0.85 m** wide and the
robot is 0.42 m wide. That sets the inflation radius (0.45 m with
`cost_scaling_factor` 4.0): the centre of a doorway is not lethal and still has a
low enough cost for the planner to go through it.

### 2. Map loading (`map_server`)
`map_loader.launch.py` runs `nav2_map_server/map_server` and its own lifecycle
manager. The map path comes in through the `map` launch argument and is injected into
the parameter file with `nav2_common.launch.RewrittenYaml`, so no absolute paths
are hard-coded.

### 3. Localization (`amcl`)
* `DifferentialMotionModel`. The alpha values are low (0.1) because simulated odometry is accurate.
* `likelihood_field` laser model, 60 beams, `laser_max_range` 12 m to match the sensor.
* `set_initial_pose: true` with the spawn pose, so AMCL localizes as soon as it starts.
* Filter updates after 0.10 m or 0.15 rad of motion.

AMCL publishes `map → odom`. Gazebo's diff-drive publishes `odom → base_footprint`,
and robot_state_publisher publishes the rest of the TF tree.

### 4. Navigation (Nav2 plugins)
Only basic navigation is needed, so I chose simple, robust plugins:

| Server | Plugin(s) | Why |
|--------|-----------|-----|
| planner_server | `nav2_navfn_planner/NavfnPlanner` (A*) | simple, reliable for a 2D grid map |
| controller_server | `RegulatedPurePursuitController`, `SimpleProgressChecker`, `SimpleGoalChecker` | good path tracking for diff drive, few parameters, slows down near obstacles and in turns, rotates to heading in place |
| behavior_server | `Spin`, `BackUp`, `Wait` | recovery actions used by the BT |
| bt_navigator | custom BT `navigate_to_pose_testbed.xml` | replans at 1 Hz, follows the path; on failure clears costmaps → spin → wait → back up (round-robin, 6 retries) |
| velocity_smoother | open-loop smoothing | limits acceleration, so the robot doesn't jerk at the wheels |
| costmaps | global: static + obstacle + inflation, local (3×3 m rolling): obstacle + inflation | the obstacle layer marks objects that are not in the static map |

The velocity pipeline is:
`controller_server / behavior_server → /cmd_vel_nav → velocity_smoother → /cmd_vel → Gazebo diff-drive`.

Each launch file declares its own parameter-file argument (`map_params_file`,
`amcl_params_file`, `nav2_params_file`). ROS 2 Humble launch configurations are not
scoped across `IncludeLaunchDescription`, so a shared `params_file` name would leak
from one included file into another.

## Results

Tested headless (gzserver, Cyclone DDS) with the full stack:

* all lifecycle nodes reach **active**
* `send_goal.py --tour`: **5/5 goals reached** (≈ 40 m, through both doorways,
  about 1.5 minutes)
* AMCL estimate vs. Gazebo ground truth after the tour: **≈ 8 cm** error

Demo video: [media/nav_video.mp4](media/nav_video.mp4) (4x-speed preview: [media/nav_preview.gif](media/nav_preview.gif)).

## Challenges

1. **The robot kept spinning slowly while idle.** Odom yaw crept from 0 to 0.8 rad with no
   `cmd_vel`. The wheel joints were not moving, so the chassis was sliding. The cause was six
   coplanar mesh contacts (2 wheels + 4 fixed caster meshes) plus frictionless casters. Sphere
   casters 2 mm above the ground and cylinder wheels fixed it.
2. **Poor localization.** The lidar range was only 1.5 m, while the rooms are up to 10 m
   across. Raising it to 12 m gave AMCL enough features to match.
3. **Launch-argument leakage.** Including `map_loader.launch.py` from
   `localization.launch.py` made both see the same `params_file` value. Unique argument names
   fixed it.
4. **Sim time.** robot_state_publisher ran on wall-clock time, which caused TF extrapolation
   errors in Nav2. It now runs with `use_sim_time`.

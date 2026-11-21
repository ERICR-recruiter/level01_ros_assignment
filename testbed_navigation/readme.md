# testbed_navigation

Nav2 navigation for the Testbed robot (ROS 2 Humble, Gazebo Classic). Each Nav2
piece (map server, AMCL, planner, controller, behaviors, BT navigator) is started
by hand instead of using `nav2_bringup`.

## Files

```
testbed_navigation/
├── config/
│   ├── amcl_params.yaml      # AMCL settings
│   └── nav2_params.yaml      # planner, controller, costmaps, behaviors,
│                             #   waypoint follower, velocity smoother, collision monitor
├── launch/
│   ├── map_loader.launch.py      # loads the map
│   ├── localization.launch.py    # map + AMCL
│   ├── navigation.launch.py      # Nav2 servers
│   └── bringup_all.launch.py     # Gazebo + robot + everything + RViz
├── rviz/navigation.rviz      # saved RViz layout
├── scripts/patrol.py         # drives the robot through 3 waypoints
└── docs/tf_tree.pdf          # TF tree
```

## Run

```bash
ros2 launch testbed_navigation bringup_all.launch.py
```

Wait about 20 s for RViz, then set goals with **2D Goal Pose**, or run the patrol:

```bash
ros2 run testbed_navigation patrol.py --ros-args -p use_sim_time:=true
```

Each part can also be launched alone: `map_loader`, `localization`, `navigation`.

## What each launch file starts

| Launch file | Starts |
|---|---|
| `map_loader` | `map_server` |
| `localization` | map loader + `amcl` |
| `navigation` | `planner_server`, `controller_server`, `behavior_server`, `bt_navigator`, `waypoint_follower`, `velocity_smoother`, `collision_monitor` |
| `bringup_all` | all of the above + Gazebo, robot and RViz |

## Command path

```
controller -> /cmd_vel_nav -> velocity_smoother -> /cmd_vel_smoothed
           -> collision_monitor -> /cmd_vel -> robot
```

The smoother limits acceleration. The collision monitor stops the robot if the
lidar sees an obstacle inside a box around it.

## Main choices

- Global planner: NavFn. Local controller: DWB.
- Max speed 0.26 m/s linear, 1.0 rad/s angular.
- Waypoint follower keeps going if one waypoint fails.

See the repository root README for the full explanation, architecture diagram and
debugging log, and `BUGS.md` for the starter-code fixes.
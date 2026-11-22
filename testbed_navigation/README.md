# testbed_navigation

Manual Nav2 setup for the Testbed-T1.0.0 robot (ROS 2 Humble, Gazebo 11).
Instead of nav2_bringup, map loading, localization and navigation each have
their own launch file and parameter file, so every part can be started and
tested on its own.

Demo video: VIDEO_LINK

## Package structure

    testbed_navigation/
    ├── launch/
    │   ├── map_loader.launch.py     # map_server + lifecycle manager
    │   ├── localization.launch.py   # amcl + lifecycle manager
    │   └── navigation.launch.py     # planner, controller, behaviors, bt_navigator + lifecycle manager
    ├── config/
    │   ├── amcl_params.yaml
    │   └── nav2_params.yaml
    └── rviz/
        └── nav.rviz

## How to run

    cd ~/assignment_ws && colcon build && source install/setup.bash
    export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp   # recommended in help.md

Then in four terminals, in this order:

    ros2 launch testbed_bringup testbed_full_bringup.launch.py   # Gazebo + RViz
    ros2 launch testbed_navigation map_loader.launch.py          # map
    ros2 launch testbed_navigation localization.launch.py        # AMCL
    ros2 launch testbed_navigation navigation.launch.py          # Nav2 servers

In RViz set Fixed Frame to `map` (or open rviz/nav.rviz).

## 1. Map loading

`nav2_map_server` loads `testbed_bringup/maps/testbed_world.yaml`
(405 x 400 cells at 0.05 m) and publishes `/map`. map_server is a lifecycle
node, so a separate `lifecycle_manager_map` configures and activates it.
The map is published once with transient-local QoS, so the RViz Map display
must use Durability = Transient Local.

## 2. Localization (AMCL)

`config/amcl_params.yaml`:
- `robot_model_type: nav2_amcl::DifferentialMotionModel` (diff drive robot)
- `base_frame_id: base_footprint`, `odom_frame_id: odom`, `global_frame_id: map`
- `scan_topic: scan`, `laser_max_range: 10.0` (same as the fixed lidar range)
- `set_initial_pose: true` at x=0.0, y=5.0, yaw=0.0, which is where
  spawn_testbed.launch.py places the robot, so no manual pose estimate is needed.

AMCL publishes the `map -> odom` transform. Check with:

    ros2 run tf2_ros tf2_echo map odom

## 3. Navigation

`config/nav2_params.yaml` starts from the Humble default params, changed for this robot:
- `robot_base_frame: base_footprint` in both costmaps (the robot's root frame)
- `robot_radius: 0.25` (base is roughly 0.35 m x 0.4 m)
- `use_sim_time: True` everywhere

Plugins (kept simple, as only basic navigation is needed):
- Planner: `nav2_navfn_planner/NavfnPlanner`
- Controller: DWB (`dwb_core::DWBLocalPlanner`)
- Behaviors: spin, backup, drive_on_heading, wait
- BT navigator: default navigate_to_pose_w_replanning_and_recovery tree
- Costmaps: static, obstacle (from /scan) and inflation layers

`lifecycle_manager_navigation` brings up controller_server, planner_server,
behavior_server and bt_navigator.

## Sending goals

From RViz: **2D Goal Pose**.

From the terminal, calling the action directly:

    ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
      "{pose: {header: {frame_id: map}, pose: {position: {x: 0.0, y: 5.0}, orientation: {w: 1.0}}}}"

## Challenges

- **No laser points in RViz:** the lidar range was only 1.5 m, so walls were out of view. Raised to 10 m.
- **TF / time problems:** robot_state_publisher was not using sim time. Added use_sim_time.
- **Map not shown in RViz:** the Map display needed Transient Local durability, because map_server publishes the map only once.
- **RViz could not see the Nav2 topics:** terminals were not all sourced the same way. Fixed by stopping the ROS daemon and sourcing install/setup.bash in every terminal.
- **Nothing happens until lifecycle nodes are activated:** every Nav2 node needs a lifecycle manager with autostart.

Full list of starter-code bugs: `../bugs_fixed.txt`.

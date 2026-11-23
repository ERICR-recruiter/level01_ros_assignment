# testbed_navigation

Manual Nav2 workflow for the **Testbed-T1.0.0** robot - no `nav2_bringup`.
Each Nav2 component is started from its own launch file with its own parameters.

```
testbed_navigation/
├── config/
│   ├── map_server_params.yaml   # map_server
│   ├── amcl_params.yaml         # AMCL
│   └── nav2_params.yaml         # planner, controller, costmaps, BT navigator, behaviours, waypoint follower
├── launch/
│   ├── map_loader.launch.py     # map_server + lifecycle manager
│   ├── localization.launch.py   # amcl + lifecycle manager
│   ├── navigation.launch.py     # planner / controller / behavior / bt_navigator / waypoint_follower + lifecycle manager
│   ├── rviz.launch.py           # RViz with a navigation layout (optional)
│   └── bringup_all.launch.py    # includes the 3 launch files above (+ RViz)
└── rviz/navigation.rviz
```

## Build and run

```bash
cd ~/assignment_ws && colcon build --symlink-install && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp      # recommended in help.md

# terminal 1 - simulation (Gazebo + robot + RViz)
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# terminal 2 - 1) map
ros2 launch testbed_navigation map_loader.launch.py
# terminal 3 - 2) localisation
ros2 launch testbed_navigation localization.launch.py
# terminal 4 - 3) navigation
ros2 launch testbed_navigation navigation.launch.py
# terminal 5 - RViz with the navigation layout (or switch the fixed frame to `map` in the existing RViz)
ros2 launch testbed_navigation rviz.launch.py
```
Or terminals 2-5 in one go: `ros2 launch testbed_navigation bringup_all.launch.py`.

Send a goal with the **2D Goal Pose** tool in RViz, or from the CLI:
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 5.0}, orientation: {w: 1.0}}}}"
```

## Approach

* **Map loading** - `nav2_map_server` is a lifecycle node; `lifecycle_manager_map` configures/activates it. The map path defaults to `testbed_bringup/maps/testbed_world.yaml` and can be overridden with `map:=`.
* **Localisation** - AMCL with the likelihood-field laser model and the differential motion model. Frames: `map -> odom` (AMCL), `odom -> base_footprint` (Gazebo diff-drive plugin), lidar on `/scan`. The initial pose equals the Gazebo spawn pose (0, 5, yaw 0) so the filter converges immediately; it can be re-set with RViz *2D Pose Estimate*.
* **Navigation** - NavFn global planner, DWB local planner (`FollowPath`), static + obstacle + inflation layers in the global costmap, obstacle + inflation in the rolling local costmap, `bt_navigator` with the default NavigateToPose tree and the spin/backup/wait recoveries, plus `waypoint_follower`. Only basic functionality, so `velocity_smoother` and `collision_monitor` are not used.
* **Robot size** - taken from the meshes: ~0.36 x 0.41 m, rotating about the wheel axle; a 0.30 m radius is used for both costmaps. Doorways in the map are ~0.9 m wide, so the robot fits.
* Speeds/accelerations are deliberately gentle (0.26 m/s, 1 m/s^2) because wheel/ground friction is limited in Gazebo.

## Bugs found in the starter code
See `BUGS_AND_FIXES.txt` in the repository root.

## Challenges
* The starter code had several intentional bugs (wrong map path, maps not installed, `ament_package` without parentheses, world file never passed to Gazebo, ROS 1 plugin, 1.5 m lidar range ...) that had to be fixed before anything could be tested.
* Lifecycle ordering: AMCL and the costmaps need `/map` (transient-local), so the map is started first; the separate lifecycle managers keep each component restartable on its own.

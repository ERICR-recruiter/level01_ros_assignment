# `testbed_navigation`

Modular ROS 2 Humble Nav2 navigation package for the ERIC Robotics **Testbed-T1.0.0** robot. Rather than invoking `nav2_bringup`, each navigation subsystem is configured and launched independently with its own parameter file and lifecycle manager.

## Package Contents

- `config/map_server_params.yaml` — Map Server and `lifecycle_manager_map` parameters.
- `config/amcl_params.yaml` — AMCL particle filter, differential motion model, and 12 m LiDAR likelihood-field parameters (`set_initial_pose: false` so initial pose is explicitly verified via RViz2).
- `config/nav2_params.yaml` — Nav2 Humble configuration for `bt_navigator` (with 47 Humble `plugin_lib_names`), `controller_server` (`RegulatedPurePursuitController`), `local_costmap` / `global_costmap` (exact STL-measured polygon footprint `[[-0.24, -0.25], [-0.24, 0.18], [0.14, 0.18], [0.14, -0.25]]`, `inflation_radius: 0.45`), `planner_server` (`NavfnPlanner` with A\*), `smoother_server` (`SimpleSmoother`), `behavior_server` (`Spin`, `BackUp`, `DriveOnHeading`, `Wait`), and `lifecycle_manager_navigation`.
- `launch/map_loader.launch.py` — Standalone map loader (`testbed_bringup/maps/testbed_world.yaml`).
- `launch/localization.launch.py` — Standalone AMCL localization launcher.
- `launch/navigation.launch.py` — Standalone Nav2 navigation servers launcher.
- `launch/bringup_navigation.launch.py` — Staged convenience launcher starting map, localization, navigation, and RViz2 in sequence.
- `rviz/nav2_view.rviz` — Preconfigured RViz2 layout displaying Map, LaserScan, AMCL particles, Global/Local Costmaps, Global/Local Plans, Robot Footprint, and TF.

## Approach & Challenges

1. **Starter Code Bugs**: Before tuning Nav2, several starter defects had to be resolved in `testbed_description`, `testbed_gazebo`, and `testbed_bringup` (see `../BUGS_FIXED.md`), most notably a 1.5 m LiDAR max range that prevented AMCL from seeing walls, a ROS 1 `libgazebo_ros_control.so` plugin, a malformed `>>` tag in the IMU plugin, missing `use_sim_time` in `robot_state_publisher`, uninstalled Gazebo `models/`, and a 0.35 m vs. 0.376 m wheel separation mismatch.
2. **Accurate Footprint Modeling**: Inspecting the binary STL meshes showed the chassis and wheels are slightly offset from `base_link` origin (`X in [-0.226, +0.124]`, `Y in [-0.241, +0.165]`). Switching from a provisional circular radius to an exact padded polygon footprint ensures accurate obstacle clearance through the 0.90 m doorways in `testbed_playground.world`.
3. **ROS 2 Humble Compatibility**: Plugin names (`nav2_navfn_planner/NavfnPlanner`, `nav2_behaviors/Spin`, etc.) and the explicit `bt_navigator` `plugin_lib_names` list are pinned specifically to ROS 2 Humble APIs.

See `../RUN_INSTRUCTIONS.md` and `../TEST_REPORT.md` for full execution and verification instructions.

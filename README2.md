# testbed_navigation

Manual Nav2 navigation stack for the Testbed-T1.0.0 robot, built by wiring individual `nav2` plugins directly rather than using `nav2_bringup`.

## Approach

Navigation is split into three independent launch files, each responsible for one stage of the pipeline:

1. **`map_loader.launch.py`** — starts `nav2_map_server` and its own `lifecycle_manager`, loading the map from `testbed_bringup/maps/testbed_world.yaml`.
2. **`localization.launch.py`** — starts `nav2_amcl` with parameters from `config/amcl_params.yaml`, plus a `lifecycle_manager` to activate it.
3. **`navigation.launch.py`** — starts `controller_server`, `planner_server`, `behavior_server`, and `bt_navigator`, all loading `config/nav2_params.yaml`, plus a `lifecycle_manager_navigation` that activates all four in sequence.

Each stage is launched independently, which matches the assignment's goal of exercising the `nav2` plugins directly rather than as one monolithic bringup.

## Plugin choices

Kept intentionally simple, per the assignment's note that "only basic navigational functionality is expected":

- **Controller:** `dwb_core::DWBLocalPlanner` — mature, well-documented, good default critic set for basic obstacle-aware path following.
- **Planner:** `nav2_navfn_planner/NavfnPlanner` — simplest reliable 2D global planner; no need for Smac/Hybrid planning on a flat, non-kinematically-constrained testbed.
- **Behaviors:** `Spin`, `BackUp`, `Wait` from `nav2_behaviors` — standard basic recovery set.
- **BT:** default Nav2 behavior tree (`navigate_to_pose_w_replanning_and_recovery.xml`) — replanning + recovery, no custom tree needed for this scope.
- `velocity_smoother` and `collision_monitor` were left out to keep the setup basic, but the params file has them commented out and ready to enable if extended later.

## Footprint

`robot_radius` in both costmaps is set to `0.3`, calculated from the URDF's caster joint origins rather than guessed. The furthest caster (`caster_2`, at (-0.176, -0.184) relative to `base_link`) sits ~0.255 m from center; adding a small buffer for the caster's own body gives ~0.3 m. This is a conservative circular approximation — the robot's actual footprint is asymmetric (offset further back-left than front-right, because of the caster layout), so the circle is oversized at three corners and exact at the fourth. A polygon footprint would be more precise, but a circular `robot_radius` was sufficient for basic obstacle avoidance at this stage.

## Testing performed

1. `map_loader.launch.py` launched, map confirmed loading correctly in RViz (occupancy grid visible, matches physical walls in Gazebo).
2. `localization.launch.py` launched, 2D pose estimate set in RViz, AMCL particle cloud converged to a tight cluster around the robot's true pose.
3. `navigation.launch.py` launched — all four lifecycle nodes (`controller_server`, `planner_server`, `behavior_server`, `bt_navigator`) confirmed `active` via `ros2 lifecycle get`.
4. Goal sent via `ros2 action send_goal /navigate_to_pose ...` — global path planned, `controller_server` continuously replanned/followed the path, robot drove to the goal, and `bt_navigator` reported `Goal succeeded`.
5. Goal sent via RViz's "2D Goal Pose" tool (which publishes to `/goal_pose`, consumed directly by `bt_navigator`) — robot successfully navigated to the clicked point.

## Challenges faced

- **Pluginlib class name format (Humble-specific):** `nav2_navfn_planner::NavfnPlanner` and `nav2_behaviors::Spin`/`BackUp`/`Wait` (the `::` separator) are only valid from Iron onward. Humble requires the `/` separator (`nav2_navfn_planner/NavfnPlanner`, `nav2_behaviors/Spin`, etc.). Using the wrong format caused `planner_server` and, separately, `behavior_server` to fail on activation with a pluginlib "class does not exist" error, which in turn aborted the entire lifecycle bringup (the manager brings nodes up in `node_names` order and stops on first failure).
- **`$(find-pkg-share ...)` in a YAML params file:** this launch-substitution syntax is only resolved inside XML-format launch files, not when it appears as a plain string in a YAML parameters file. `bt_navigator`'s default BT XML paths therefore failed to open ("Couldn't open input XML file: $(find-pkg-share ...)"). Fixed by resolving the actual path with `get_package_share_directory('nav2_bt_navigator')` inside the Python launch file and passing it as an override parameter (which takes precedence over the unresolved string still present in the YAML).
- **Diagnosing lifecycle failures:** since `lifecycle_manager` aborts the whole bringup on the first node that fails to activate, `ros2 lifecycle get /<node_name>` for each managed node was the fastest way to isolate exactly which node was stuck and at what state, rather than re-reading the full launch log each time.
- **RViz's "Nav2 Goal" tool vs. "2D Goal Pose":** initially assumed these were interchangeable. "2D Goal Pose" publishes a `PoseStamped` to `/goal_pose`, which `bt_navigator` subscribes to directly and converts into a full `navigate_to_pose` action call — this worked immediately. The dedicated "Nav2 Goal" action-client tool was intermittently unresponsive; since `/navigate_to_pose` was independently confirmed working via both `/goal_pose` and a direct `ros2 action send_goal` call, this was isolated to an RViz tool-side quirk rather than a fault in the navigation stack itself.

## Contact Info 
 - Name: Rushil Kapoor
 - Contact number: 7834981952
 - Email Address: kapoorrushil11@gmail.com
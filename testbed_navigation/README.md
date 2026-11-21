# testbed_navigation

This package contains the modular Nav2 navigation setup for the Testbed-T1.0.0 robot.

### Files
- `launch/map_loader.launch.py`: Loads the map using `nav2_map_server` and activates it with `nav2_lifecycle_manager`.
- `launch/localization.launch.py`: Launches `map_server` and `nav2_amcl` together under one lifecycle manager.
- `launch/navigation.launch.py`: Starts `controller_server`, `planner_server`, `behavior_server`, and `bt_navigator`.
- `config/amcl_params.yaml`: AMCL settings with differential motion model and spawn initial pose `(x: 0.0, y: 5.0)`.
- `config/nav2_params.yaml`: Costmaps, Navfn global planner, and DWB local planner configurations.

### Key challenges & notes
- Doorway width is around 0.85m in the world. With default 0.45m inflation radius, the door gets closed off in the global costmap and forces the robot into a long detour. Tuned `robot_radius: 0.20` and `inflation_radius: 0.30` to let it path cleanly through doorways.
- QoS durability for the map subscriber in RViz must be set to `Transient Local` to receive the latched map.


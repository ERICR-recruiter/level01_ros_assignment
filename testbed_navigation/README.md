# Testbed Navigation Setup

This package adds the map-loading, localization, and navigation flow for the Testbed robot using Nav2 components.

## Map loading

Run:

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

This starts the `nav2_map_server` and loads the occupancy map from `testbed_bringup/maps/testbed_world.yaml`.

## Localization

Run:

```bash
ros2 launch testbed_navigation localization.launch.py
```

This starts AMCL against the loaded map and exposes the robot pose in the `map` frame.

## Navigation

Run:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

This starts the Nav2 controller, planner, BT navigator, and recovery servers. Once the robot is localized, it can accept goals in RViz and plan a route through the map.

## Notes

- The map image reference in `testbed_bringup/maps/testbed_world.yaml` was corrected from the broken placeholder name to `testbed_world.pgm`.
- The main robot base frame is `base_footprint`, which matches the URDF and AMCL configuration.

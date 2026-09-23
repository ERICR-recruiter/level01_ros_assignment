# testbed_navigation

Manually-assembled Nav2 workflow for the `Testbed-T1.0.0` robot: three
independent launch files (map loading, localization, navigation) built from
individual `nav2` plugin nodes rather than `nav2_bringup`.

## Package layout

```
testbed_navigation/
├── config/
│   ├── amcl_params.yaml     # AMCL localization parameters
│   └── nav2_params.yaml     # controller/planner/behavior/bt_navigator/velocity_smoother params
├── launch/
│   ├── map_loader.launch.py   # nav2_map_server + lifecycle_manager
│   ├── localization.launch.py # nav2_amcl + lifecycle_manager
│   └── navigation.launch.py   # controller_server, planner_server, behavior_server,
│                               # bt_navigator, velocity_smoother + lifecycle_manager
├── CMakeLists.txt
└── package.xml
```

## Approach

Each stage of the navigation pipeline is its own launch file with its own
`nav2_lifecycle_manager` instance, so every stage can be brought up and
tested independently (per the assignment's "test components independently"
guideline), or chained together from `testbed_bringup` later.

1. **Map loading** (`map_loader.launch.py`) — runs `nav2_map_server`
   against `testbed_bringup/maps/testbed_world.yaml` and its own
   `lifecycle_manager_map_server` to configure/activate it.
2. **Localization** (`localization.launch.py`) — runs `nav2_amcl` against
   `config/amcl_params.yaml` with its own `lifecycle_manager_localization`.
   Requires `map_loader.launch.py` (or an equivalent map publisher) to
   already be active, since AMCL subscribes to the `/map` topic rather than
   loading the map itself.
3. **Navigation** (`navigation.launch.py`) — runs `controller_server`
   (DWB local planner), `planner_server` (NavFn global planner),
   `behavior_server` (spin/backup/wait recoveries), `bt_navigator`
   (default `navigate_to_pose`/`navigate_through_poses` behavior trees
   shipped with `nav2_bt_navigator`) and `velocity_smoother`, all managed
   by `lifecycle_manager_navigation`. Requires localization to be active
   for `bt_navigator`'s `map -> odom -> base_footprint` TF chain.

Typical bring-up order once the robot is spawned via
`testbed_bringup testbed_full_bringup.launch.py`:

```bash
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
ros2 launch testbed_navigation navigation.launch.py
```

Set an initial 2D pose estimate in RViz (or rely on the `set_initial_pose`
default baked into `amcl_params.yaml`, which matches the robot's spawn pose)
before sending a Nav2 goal.

## Frame/topic choices

These were taken directly from `testbed_description/urdf/testbed.gazebo`
so the params line up with what the `libgazebo_ros_diff_drive.so` and lidar
plugins actually publish:

- `odom_frame_id` / `global_frame` (local costmap): `odom`
- `base_frame_id` / `robot_base_frame`: `base_footprint`
- `scan_topic` / costmap obstacle source: `scan`
- AMCL `initial_pose`: `x=0.0, y=5.0, yaw=0.0`, matching the spawn pose in
  `testbed_gazebo/launch/spawn_testbed.launch.py`.
- Laser/costmap max range: `12.0 m`, matching the corrected lidar range in
  `testbed.gazebo` (see `../BUGS_AND_FIXES.md`) — the map is ~20 m x 20 m,
  so a longer-range costmap sees enough of the environment to plan through it.
- Robot footprint approximated as a `0.5 m x 0.4 m` rectangle from the
  caster/wheel offsets in `testbed.xacro` (no exact footprint was provided).

Only the "basic" Nav2 plugin set was used per the assignment scope: NavFn
for global planning, DWB for local control, and the default spin/backup/wait
recovery behaviors — no Smac/Hybrid-A*, keepout costmap layers, or
collision monitor, since those aren't required for basic point-to-point
navigation on this map.

## Challenges / notes

- The starter code had a map file path typo and a malformed XML tag in the
  Gazebo IMU plugin block that had to be fixed before the robot description
  would even parse — see `../BUGS_AND_FIXES.md` for the full list.
- `testbed_bringup` and `testbed_gazebo`'s `CMakeLists.txt` files were not
  installing the `maps/` and `models/` directories, respectively, so a clean
  `colcon build` would leave the map file and custom Gazebo models
  unreachable from the install space — this package's `map_loader.launch.py`
  depends on `testbed_bringup`'s installed `maps/` directory, so that fix
  was required for `map_loader.launch.py` to find the map at all.
- Because this was written and reviewed without a build/run pass (time
  constraint — see submission note), parameter values (footprint,
  DWB gains, costmap sizes) are reasoned from the URDF/geometry and standard
  Nav2 Humble defaults rather than empirically tuned. They're a reasonable
  starting point but should be verified/tuned against the running
  simulation.

# testbed_navigation

Manual Nav2 bringup for the **Testbed-T1.0.0** robot. Instead of calling
`nav2_bringup`, each piece of the navigation workflow (map loading, localization,
navigation) is launched by hand from its own launch file, using the individual
Nav2 plugins.

## Approach

Nav2's servers are **lifecycle nodes** — they do nothing until something walks
them through `configure → activate`. In every launch file I pair the Nav2 nodes
with a `nav2_lifecycle_manager` set to `autostart: true`, which does exactly
that. This is the single most important idea behind the whole package.

The workflow is split so each stage can be tested on its own (KISS):

| Stage | Launch file | Nodes brought up |
|-------|-------------|------------------|
| Map loading  | `map_loader.launch.py`   | `map_server` |
| Localization | `localization.launch.py` | `map_server`, `amcl` |
| Navigation   | `navigation.launch.py`   | `controller_server`, `planner_server`, `behavior_server`, `bt_navigator`, `velocity_smoother` |
| Everything   | `bringup.launch.py`      | localization + navigation + RViz |

## Config

- `config/amcl_params.yaml` — AMCL only. Differential motion model, seeded with
  the robot's Gazebo spawn pose `(0, 5)` so it localizes without a manual pose
  estimate.
- `config/nav2_params.yaml` — everything else: NavFn global planner (Dijkstra),
  DWB local planner, the standard spin/backup/wait behaviours, the BT navigator,
  and a velocity smoother.

## Plugin choices (and why)

- **map_server** — serves the static `testbed_world` map.
- **AMCL** — particle-filter localization; publishes the `map → odom` transform.
- **NavFn planner** — a Dijkstra grid planner. The task only needs basic point
  A → B navigation, so a full kinematic planner would be overkill.
- **DWB controller** — samples candidate velocities and scores them with critics.
  Easy to explain and tune, and handles a diff-drive robot well.
- **behavior_server** — recovery behaviours (spin, back up, wait) for when the
  robot gets stuck.
- **velocity_smoother** — sits between the controller and the robot so the
  `/cmd_vel` sent to Gazebo is acceleration-limited and smooth.

## Topic wiring

Controller output `cmd_vel` is remapped to `cmd_vel_nav`; the velocity smoother
reads `cmd_vel_nav` and publishes the final `cmd_vel`, which the Gazebo
diff-drive plugin drives on.

## Running

```bash
# Terminal 1 - simulator + robot
ros2 launch testbed_bringup testbed_full_bringup.launch.py

# Terminal 2 - localization + navigation + RViz
ros2 launch testbed_navigation bringup.launch.py
```

Or run the stages individually with `map_loader.launch.py`,
`localization.launch.py`, and `navigation.launch.py`.

Send a goal from RViz with the **Nav2 Goal** tool, or from the CLI by publishing
to `/goal_pose`.
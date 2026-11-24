# testbed_navigation

Manual Nav2 bringup for the Testbed-T1.0.0 robot. Instead of using `nav2_bringup`, this package starts each Nav2 piece separately, with its own launch file and parameter file.

| Step | Launch file | Parameters | Status |
|------|-------------|------------|--------|
| Map loading | `launch/map_loader.launch.py` | `config/map_server_params.yaml` | In progress |
| Localization | `launch/localization.launch.py` | `config/amcl_params.yaml` | To do |
| Navigation | `launch/navigation.launch.py` | `config/nav2_params.yaml` | To do |

---

## How to run
*(filled in as each launch file is finished)*

```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py   # simulation
```

---

## Approach

### 1. Make the starter simulation healthy first
Nav2 can only work if the robot, sensors, TF and map are correct, so I fixed the starter code before writing anything new. I ran each part and checked it with ROS tools instead of assuming it worked:
- `colcon build` output and logs
- `ros2 topic hz` / `echo` on `/scan` and `/odom`
- `ros2 param get` for `use_sim_time`
- the Gazebo server log for plugin errors
- the installed `share/` folders compared with the source
- running `map_server` on its own to test the map
- driving with `teleop_twist_keyboard`

I found and fixed **8 bugs**. They are all documented in [`../BUGS.md`](../BUGS.md).

### 2. Refresh the Nav2 concepts
I had used Nav2 about a year ago, so I re-read the [Nav2 concepts docs](https://docs.nav2.org/concepts/index.html) before starting. The key ideas for this package:
- **Nav2 is a set of separate servers.** map_server publishes the map. AMCL finds where the robot is on it. planner_server plans the path. controller_server follows it and sends `/cmd_vel`. behavior_server runs recoveries (spin, back up, wait). bt_navigator decides when to call each one.
- **Lifecycle nodes.** Nav2 nodes go through *unconfigured → inactive → active*. Parameters load in *configure*, but data only flows once the node is *active*. A **lifecycle manager** steps the nodes through these states in order, so for example the map exists before AMCL needs it.
- **TF chain:** `map → odom → base_footprint → lidar_link_1`. The simulation provides everything below `odom`. AMCL adds `map → odom`.

### 3. Package design
- An `ament_cmake` package with only `launch/`, `config/` and `rviz/`. It has no source code, because Nav2's executables already exist. The job is to start them with the right parameters and connect them.
- There is one launch file and one parameter file per step, and each step has its own lifecycle manager, so every step can be started and tested on its own.

### 4. Map loading *(in progress)*
`map_loader.launch.py` starts map_server and its lifecycle manager, with `use_sim_time` and the map path as launch arguments.

---

## Challenges

| Challenge | How I solved it |
|-----------|-----------------|
| **Bugs that give no error.** The lidar published at 30 Hz and looked fine, but every reading was `inf`, because its max range was 1.5 m and the nearest wall is about 3.4 m away. | I checked the actual data with `ros2 topic echo /scan`, not just whether the topic existed. I set the range to 12 m. |
| **A ROS 1 plugin left in the URDF.** `libgazebo_ros_control.so` doesn't exist in ROS 2, and it only shows up in the Gazebo log. | I read the Gazebo server log, then removed the plugin, since `diff_drive` already drives the robot. |
| **Wrong clock.** robot_state_publisher used wall time while Gazebo used sim time, which causes TF timing errors in Nav2. | I checked every node with `ros2 param get <node> use_sim_time`. |
| **My own XML mistake.** I wrote `<exec_depend/>` instead of `</exec_depend>` in `package.xml`, and the build failed with `mismatched tag`. | Fixed the tags. I now run `xmllint --noout package.xml` before building. |

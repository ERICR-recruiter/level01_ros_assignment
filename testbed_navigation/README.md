# testbed_navigation

ROS2 Nav2 navigation package for the Testbed-T1.0.0 robot.

The navigation stack is split into three launch files so each part can be tested independently:

```text
map_loader.launch.py
    map_server + lifecycle manager

localization.launch.py
    AMCL + lifecycle manager
    └── includes map_loader

navigation.launch.py
    planner + controller + smoother
    behavior server + BT navigator
    velocity smoother + lifecycle manager
    └── includes localization
```

## How I worked through it

### 1. Ported the project to Jazzy

The assignment was provided for ROS2 Humble/Ubuntu 22.04, while I was working on Ubuntu 24.04 with ROS2 Jazzy. I decided to port the project instead of using a Docker environment.

The changes are documented in [`MIGRATION.md`](../MIGRATION.md).

### 2. Checked the robot before Nav2

Before debugging navigation, I checked the basic things Nav2 depends on:

* `/scan`
* `/odom`
* `/joint_states`
* TF tree
* `cmd_vel`

I also manually published velocity commands to make sure the robot could actually move.

### 3. Found a lidar configuration issue

The lidar was publishing valid scans, but its configured range was much smaller than the size of the map. This meant the data was not very useful for AMCL even though the topic itself looked healthy.

This was one of the bugs documented in [`BUGS.md`](../BUGS.md).

### 4. Built Nav2 bottom-up

I built the stack in stages:

```text
Map → Localization → Navigation
```

I kept separate launch files so I could test each stage independently. This made debugging much easier than having one large launch file and trying to figure out which component was failing.

### 5. Tested with navigation goals

Once everything was running, I used RViz to set initial poses and send multiple 2D navigation goals.

I checked that the robot could plan a path, follow it and reach the requested goal.

---

## Running

Start the simulation:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py rviz:=false
```

Then start navigation:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Use RViz's **2D Pose Estimate** and **2D Goal Pose** tools to localize and navigate the robot.

---

## Plugin choices

| Component        | Plugin                                           |
| ---------------- | ------------------------------------------------ |
| Global planner   | `nav2_navfn_planner::NavfnPlanner`               |
| Local controller | `dwb_core::DWBLocalPlanner`                      |
| Behaviors        | `Spin`, `BackUp`, `DriveOnHeading`, `Wait`       |
| Behavior Tree    | `navigate_to_pose_w_replanning_and_recovery.xml` |
| Smoother         | `nav2_smoother::SimpleSmoother`                  |
| Velocity         | `nav2_velocity_smoother`                         |

I chose relatively simple plugins because the assignment only required basic navigation in a small simulated environment.

---

## Some challenges

### Lidar range

The lidar was limited to around 1.5 m while the map was much larger. The scan was valid, but AMCL did not have enough useful information to localize reliably.

### TF and frame names

The robot uses `base_footprint` rather than the `base_link` commonly used in Nav2 examples. I had to make sure the controller, costmaps and behavior server all used the correct frame.

### Lifecycle nodes

Getting used to Nav2's lifecycle system took some time. A node being present did not necessarily mean it was active, so I had to check lifecycle states while debugging.

### Slow final rotation

During testing, the robot sometimes reached the goal area but took a long time to finish rotating. This turned out to be related to DWB's `RotateToGoal` critic and its velocity slowing near the goal. Adjusting the `slowing_factor` improved the final approach.

---

## What I learned

This assignment helped me understand Nav2 at a lower level instead of treating it as a single navigation package.

The main pipeline I worked with was:

```text
Sensors
  ↓
TF + Odometry
  ↓
Map + AMCL
  ↓
Costmaps
  ↓
Planner
  ↓
Controller
  ↓
Velocity Smoother
  ↓
Robot
```

The biggest takeaway for me was to debug robotics systems one layer at a time rather than trying to debug the complete stack at once.

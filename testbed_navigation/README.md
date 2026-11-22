# testbed_navigation — ROS2 Nav2 Navigation Package

## Overview
This package provides the complete navigation stack for the **Testbed-T1.0.0** robot
from ERIC Robotics, using individual `nav2` plugins as required by the Level 01
ROS2 Navigation Assignment.

Rather than calling `nav2_bringup` as a black box, each navigation component is
launched independently to demonstrate understanding of the Nav2 plugin architecture.

---

## Package Structure
```
testbed_navigation/
├── config/
│   ├── amcl_params.yaml     # AMCL localization parameters
│   └── nav2_params.yaml     # Full Nav2 stack parameters
└── launch/
    ├── map_loader.launch.py    # Step 1: Load map
    ├── localization.launch.py  # Step 2: Map + AMCL localization
    └── navigation.launch.py   # Step 3: Full navigation stack
```

---

## Robot Specifications (from URDF analysis)
| Property | Value |
|---|---|
| Drive type | Differential drive |
| Wheel separation | 0.35 m |
| Wheel diameter | 0.1 m |
| Base frame | `base_footprint` |
| LiDAR topic | `/scan` (LaserScan) |
| LiDAR range | 0.10 – 1.50 m, 300 rays, 360° |
| Odometry topic | `/odom` |
| Velocity command | `/cmd_vel` |
| IMU topic | `/imu` |
| Spawn position | x=0.0, y=5.0, z=0.0 |

---

## How to Run

### Prerequisites
```bash
# Allow Docker to access the host display
xhost +local:docker

# Build and start the Docker container
cd "Robotic Intern Assignments"
docker compose build
docker compose run --rm ros2_nav bash
```

### Inside the Container

**Step 1 — Start the simulation** (Gazebo + RViz):
```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

**Step 2 — Load the map** (in a new terminal / `docker exec`):
```bash
ros2 launch testbed_navigation map_loader.launch.py
```
Verify: The map appears in RViz as a grey/white occupancy grid.

**Step 3 — Start localization** (replaces Step 2 when navigating):
```bash
ros2 launch testbed_navigation localization.launch.py
```
Verify: Use the "2D Pose Estimate" button in RViz to set initial pose.
The particle cloud should converge around the robot.

**Step 4 — Start full navigation**:
```bash
ros2 launch testbed_navigation navigation.launch.py
```
Verify: Use the "Nav2 Goal" (or "2D Nav Goal") button in RViz.
The robot should plan a path and drive to the goal autonomously.

---

## Design Decisions

### Why AMCL?
AMCL (Adaptive Monte Carlo Localization) is the standard particle-filter
localization algorithm for ROS2 nav2. It is well-suited for the testbed
environment because:
- The map is pre-built (not SLAM), making AMCL ideal.
- The robot has a 360° LiDAR which provides good particle convergence.
- AMCL's `likelihood_field` laser model works well at short ranges (≤1.5m).

### Why NavFn (Dijkstra) for global planning?
The testbed world is a relatively simple enclosed room. Dijkstra's algorithm
(NavFn with `use_astar: false`) is reliable, complete, and optimal for static
maps. A* (`use_astar: true`) can also be used for faster planning in larger maps.

### Why DWB for local planning?
DWB (Dynamic Window Approach Biased) is the default ROS2 nav2 local planner
for differential drive robots. It samples velocity commands within kinematic
constraints and scores them against obstacle proximity, path alignment, and
goal distance — well suited for the testbed robot's constraints.

### Why CycloneDDS?
Per the assignment help.md, Fast DDS (the default) can cause Nav2 timeout
issues. CycloneDDS is explicitly recommended and provides more stable
discovery and service call behavior in Nav2 deployments.

### Velocity Smoother
Added `nav2_velocity_smoother` to prevent abrupt velocity changes that could
cause wheel slip or unstable behavior with the testbed's caster-wheel design.

---

## Challenges & Notes
- The LiDAR's short max range (1.5 m) required careful costmap tuning —
  both `raytrace_max_range` and `obstacle_max_range` were set to 1.5 m to
  match hardware limits.
- The robot spawns at y=5.0 (not origin), so the AMCL initial pose is
  pre-configured to x=0.0, y=5.0 in amcl_params.yaml.
- Six bugs were found and fixed in the starter code — see `bugs_found.txt`
  in the repository root for full details.

---

## Contact
- **Name**: Your full name
- **Contact number**: Your contact number
- **Email Address**: Your email address

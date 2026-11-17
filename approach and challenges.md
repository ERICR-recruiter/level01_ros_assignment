# testbed_navigation

## Approach

I started by checking the supplied simulation, robot movement, laser scan, and odometry. I then built the navigation setup in stages, keeping map loading, localization, and navigation in separate launch files. Each launch starts the required Nav2 nodes directly and uses a lifecycle manager to configure and activate them.

The map server loads the provided map. AMCL compares the live laser scan with that map and uses odometry to estimate the robot's position and heading. An approximate initial pose is set through RViz before sending navigation goals.

NavFn generates the global path using the map and an inflated costmap. The controller follows that path using a rolling local costmap built from laser observations. I initially used DWB, then switched to Regulated Pure Pursuit for path following while keeping NavFn as the planner.

The BT navigator connects planning, path following, and replanning. The behavior server provides spin, back-up, and wait actions for recovery. The final controller configuration uses a desired linear speed of 0.15 m/s, with collision checking enabled.

## Challenges faced

**Getting localization aligned.** An inaccurate initial position or heading could leave the laser scan misaligned with the map. The original 1.5 m laser range also sometimes showed only a short section of a straight wall, making different positions look similar to AMCL. I increased the simulated range to 8 m and adjusted the motion-noise and update settings for the simulator's odometry. A reasonable initial pose is still important.

**Following paths around corners.** NavFn could generate a route, but DWB sometimes selected zero forward speed or very small turning commands near wall tips. This led to progress failures and repeated recovery attempts. I tried a rotation shim to improve heading alignment, but it did not fully resolve the behavior. I then switched to Regulated Pure Pursuit because it can rotate toward the path before moving and slow down for sharp curves and nearby obstacles.

**Map display in Rviz.** I needed to distinguish the map frame, odometry origin, and robot frame. The odometry origin does not have to stay at the robot's position. I used the map frame for the navigation view and configured the Map display with Reliable and Transient Local QoS so it could receive the published map.

**Balancing clearance and narrow passages.** Increasing obstacle clearance helped around corners, but also made tight openings more restrictive. Both costmaps now use a 0.36 m robot radius and a 0.80 m inflation radius. Some narrow openings can still produce collision-ahead stops, particularly where the saved map and live obstacle information differ. The controller keeps collision checking enabled rather than forcing the robot through an opening.

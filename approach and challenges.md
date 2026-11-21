# Testbed Navigation

## Approach

I started by exploring the provided simulation and checking whether the robot was moving properly, whether the LiDAR was detecting its surroundings, and whether odometry was working as expected.

Once the basic setup was working, I started building the navigation system step by step. Instead of launching the entire Nav2 system at once, I divided it into three separate launch files: one for loading the map, one for localization, and one for navigation. This made it easier to understand, test, and troubleshoot each part individually.

For map loading, I used the Nav2 Map Server to load the provided map. I then configured AMCL to estimate the robot's position using the map, live LiDAR data, and odometry. Before sending a navigation goal, I had to set an approximate initial position for the robot in RViz so that it could properly identify where it was.

For path planning, I used NavFn to calculate the global path. The local costmap uses live LiDAR data to detect nearby obstacles and help the robot navigate around them. I initially tried the DWB controller, but after facing some difficulties with movement near corners, I decided to switch to Regulated Pure Pursuit (RPP).

The BT Navigator manages the overall navigation process, including planning and following paths. I also configured the Behavior Server with three recovery actions: Spin, BackUp, and Wait. These actions help the robot respond when it gets stuck or faces difficulties during navigation.

In the final configuration, I kept the desired linear speed at 0.15 m/s and enabled collision checking so that the robot would avoid moving into obstacles.

## Challenges Faced

### 1. Getting the Robot's Position Right

One of the first difficulties I faced was getting the robot's position properly aligned with the map. Sometimes, even a small error in the initial position or direction caused the LiDAR scan to look different from the map, which affected localization.

The original LiDAR range was only 1.5 m. Because of this, it could sometimes detect only a small part of a wall, making it difficult for AMCL to estimate the robot's position accurately.

To improve this, I increased the simulated LiDAR range to 8 m and adjusted the motion-noise and update settings to better match the simulator's odometry. I also learned that setting a reasonable initial pose in RViz is important for getting localization working properly.

### 2. Making the Robot Follow Paths Smoothly

Another challenge was getting the robot to follow paths properly, especially around corners.

NavFn was generating paths correctly, but the DWB controller sometimes struggled near wall edges and sharp turns. In some situations, it produced almost no forward movement, which caused the robot to stop making progress and triggered recovery attempts.

I first tried using a rotation shim to help the robot align itself before moving, but the results were not consistent enough. After experimenting with it, I decided to switch to Regulated Pure Pursuit.

This worked better for my setup because the robot could turn towards the required direction before moving and adjust its speed around sharp corners and nearby obstacles.

### 3. Fixing the Map Display in RViz

I also faced some confusion while setting up the map display in RViz. Initially, I had to understand how the `map`, `odom`, and robot frames were related.

I learned that the odometry origin does not always remain at the robot's current position, so choosing the correct fixed frame is important.

I set the fixed frame in RViz to `map` and adjusted the Map display's QoS settings to Reliable and Transient Local. After that, RViz was able to receive and display the map correctly.

### 4. Handling Obstacles and Narrow Passages

Finding the right obstacle clearance settings was another challenge. I wanted the robot to maintain a safe distance from obstacles while still being able to pass through narrow openings.

Increasing the inflation radius helped the robot stay farther away from obstacles, especially around corners. However, it also made some narrow passages difficult to navigate.

After testing different settings, I kept the robot radius at 0.36 m and the inflation radius at 0.80 m for both costmaps.

There were still situations where the robot stopped because it detected a possible collision, particularly when the saved map and live LiDAR information did not match perfectly. I decided to keep collision checking enabled rather than force the robot through these areas. I felt that preventing a collision was more important than making the robot pass through every narrow opening.

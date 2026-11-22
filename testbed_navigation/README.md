# Testbed Navigation – Manual ROS 2 Nav2 Implementation

## 1. Introduction
This package defines the modular navigation workflow for the Testbed-T1.0.0 robot under ROS 2 Humble distribution and the Navigation2 (Nav2) framework.

Instead of utilizing the conventional `nav2_bringup` package, the navigation stack will be manually initialized via separate launch files that allow controlling each Nav2 node, its parameters, lifecycle and execution.
Launch file is a file that starts multiple ROS2 nodes together, instead of opening a separate terminal and running each node manually. 

The process can be separated into the following three main stages:

1. Loading of map by Map Server.
2. Localization of the robot by AMCL.
3. Navigation by Nav2 servers and Behavior Tree plugins.

> I started with checking the provided files and understanding them. By doing this I was able to configure the bugs present it the files and solved them. The list of bugs solved is mentioned in the BUG_FIXES.txt.
> Then I studied The concepts using the Nav2 Documentation provided and Also used Youtube to understand the concept of each topic and make sure why do we require it in Navigation and what difference it makes. 
> Then started to understand and build Config folder containing the parameters for configuration of map and amcl by refering the nav2 documentation and official ROS2 website.
> Build the Launch file refering the ROS2 website.
> And did the testing and debugging challenges faced like map not visible, goal path not visible, lag in robot movement etc .
> I have attached the evidence of demonstration and screenshots under /assignment_ws/src/level01_ros_assignment/evidence/screenshot and /assignment_ws/src/level01_ros_assignment/evidence/video.

## 2. Package Structure


testbed_navigation/
├── CMakeLists.txt
├── package.xml
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
├── include/
└── src/


### Directory description

- `config/`: Contains parameter configurations for AMCL and Nav2.
- `launch/`: Contains separate launch files for map loading, localization and navigation.
- `CMakeLists.txt`: Defines the package build configuration and installs launch and configuration directories.
- `package.xml`: Declares the package dependencies, including ROS 2 launch and Nav2 packages.

The package uses the `ament_cmake` build system.

## 3. Map Loading

Load the predefined environment map provided in:
Map Server is used to load a map and publish it on ROS2 topic so that other components such as AMCL & Nav2 can use it.

`testbed_bringup/maps/testbed_world.yaml`

The map consists of:
- YAML file: Contains map data.
- PGM file: Contains the actual map image.


### Implementation

The `map_loader.launch.py` file launches:

1. Map Server (`nav2_map_server`)

- Loads the YAML map configuration.
- Reads the corresponding PGM image.
- Publishes the occupancy grid on `/map`.

2. Lifecycle Manager (`nav2_lifecycle_manager`)

- Manages the lifecycle of Map Server.
- Uses `autostart: true` to automatically configure and activate it.
- Manages the `map_server` node.

## 4. Localization Using AMCL


Estimate the robot's position and orientation within the known map.

AMCL (Adaptive Monte Carlo Localization) uses a particle-filter approach to estimate the robot's pose by combining:

- The known occupancy map.
- Laser scan measurements from `/scan`.
- Odometry information from the robot. 
- The robot's motion model.

### AMCL configuration

The parameters are defined in `config/amcl_params.yaml`.

Coordinate frames:

global_frame_id : /map - Global reference frame 
odom_frame_id : /odom - Odometry reference frame 
base_frame_id : /base_footprint - obot base frame 
scan_topic : /scan - Laser scan input 

Motion model:

`nav2_amcl::DifferentialMotionModel` is used because the robot uses differential-drive motion.

Particle filter:

min_particles : 500 - Minimum particle count 
max_particles : 2000 - Maximum particle count 
pf_err : 0.05 - Particle filter error parameter 
pf_z : 0.99 - Particle filter confidence parameter 
resample_interval : 1 - Resampling interval 

Motion update thresholds:

- `update_min_d: 0.25` – Minimum translation before an update.
- `update_min_a: 0.2` – Minimum angular movement before an update.

Laser model:

The likelihood-field laser model is used.

Important settings include:

- `laser_min_range: 0.1`
- `laser_max_range: 1.5`
- `max_beams: 60`
- `laser_likelihood_max_dist: 2.0`
- `sigma_hit: 0.2`

The sensor model weights are configured using `z_hit`, `z_short`, `z_max` and `z_rand`.

Transform settings:

- `tf_broadcast: true` enables AMCL to publish the map-to-odometry transform.
- `transform_tolerance: 1.0` specifies the transform tolerance.

Initial pose:

`set_initial_pose: false` is used because the initial robot position is provided manually through RViz using the 2D Pose Estimate tool.

###Launch implementation

The `localization.launch.py` file launches:

1. AMCL using `nav2_amcl`.
2. Lifecycle Manager using `nav2_lifecycle_manager`.

The lifecycle manager automatically configures and activates AMCL.

After activation, the initial pose is provided through RViz.

## 5. Navigation Implementation



Implement autonomous navigation by manually launching the required Nav2 servers.

The implementation uses four main components.

### 5.1 Planner Server

Package: `nav2_planner`

The Planner Server calculates a global path from the robot's current position to the requested goal.

Configured planner:

`nav2_navfn_planner/NavfnPlanner`

Important parameters:

- `planner_plugins: ["GridBased"]`
- `expected_planner_frequency: 10.0`
- `tolerance: 0.5`
- `use_astar: false`
- `allow_unknown: true`

The planner uses the global costmap to calculate a path.

### 5.2 Controller Server

Package: `nav2_controller`

The Controller Server follows the global path by generating velocity commands.

Configured controller:

`dwb_core::DWBLocalPlanner`

The controller uses the DWB (Dynamic Window Based) local planning approach.

Important configuration:

- Controller frequency: 20 Hz.
- Maximum linear velocity: 0.20 m/s.
- Maximum angular velocity: 1.0 rad/s.
- Linear velocity samples: 20.
- Angular velocity samples: 20.
- Simulation time: 1.7 seconds.

DWB critics:

The following critics are configured:

1. `RotateToGoal` – Evaluates rotation behaviour near the goal.
2. `Oscillation` – Helps prevent repeated oscillating movements.
3. `BaseObstacle` – Evaluates obstacle-related trajectory costs.
4. `GoalAlign` – Evaluates alignment with the goal.
5. `PathAlign` – Evaluates alignment with the global path.
6. `PathDist` – Evaluates distance from the global path.
7. `GoalDist` – Evaluates distance to the goal.

The controller evaluates candidate trajectories using these critics and selects an appropriate trajectory.

### 5.3 Costmap Configuration

Two costmaps are configured.

Global Costmap:

- Global frame: `map`
- Robot base frame: `base_footprint`
- Resolution: 0.05 m
- Update frequency: 2 Hz
- Publish frequency: 1 Hz

Plugins:

- Static Layer: Uses the provided map.
- Obstacle Layer: Uses laser scan data to mark and clear obstacles.
- Inflation Layer: Adds a cost around obstacles.

Inflation radius: 0.35 m.

Local Costmap:

- Global frame: `odom`
- Robot base frame: `base_footprint`
- Width: 3 m
- Height: 3 m
- Resolution: 0.05 m
- Update frequency: 5 Hz
- Publish frequency: 2 Hz

The local costmap uses a rolling window and includes:

- Obstacle Layer.
- Inflation Layer.

The laser scan topic `/scan` is used as the observation source.

### 5.4 Behavior Server

Package: `nav2_behaviors`

The Behavior Server is the source of recovery behaviors which can be utilized during navigation.

There are three behaviors that are set up:

Spin : Rotation of the robot
BackUp : Reverse movement of the robot 
Wait : Pause of the robot

### 5.5 BT Navigator

Package: `nav2_bt_navigator`

The Behavior Tree Navigator manages the entire navigation task.

It interacts with the planner, controller and behavior servers via their actions.

There are plugins configured for:

- Path calculations towards poses
- Path following
- Pose navigation
- Multiple pose navigation
- Spin, Backup and Wait actions
- Costmap cleaning
- Goal and recovery conditions
- And other needed behavior tree control and condition nodes

The default navigation behavior tree XML files are provided with the installed Nav2 package.

### 5.6 Lifecycle Management

`navigation.launch.py` starts:

1. Planner Server
2. Controller Server
3. Behavior Server
4. BT Navigator
5. Lifecycle Manager

Lifecycle Manager is configured with `autostart: true` and manages all four navigation servers.

This guarantees that the nodes will be configured and started automatically.

## 6. Launch File Implementation

There are three launch files provided independently.


 `map_loader.launch.py` - Starts Map Server and its Lifecycle Manager 
 `localization.launch.py` - Starts AMCL and its Lifecycle Manager 
 `navigation.launch.py` - Starts Planner, Controller, Behavior and BT Navigator servers along with Lifecycle Manager





## 7. Build and Execution

### Step 1: Source ROS 2


source /opt/ros/humble/setup.bash


### Step 2: Build the workspace


cd ~/assignment_ws
colcon build --symlink-install

### Step 3: Source the workspace

source ~/assignment_ws/install/setup.bash


### Step 4: Launch the simulation

In Terminal 1:


ros2 launch testbed_bringup testbed_full_bringup.launch.py


### Step 5: Load the map

In Terminal 2:


ros2 launch testbed_navigation map_loader.launch.py


### Step 6: Start localization

In Terminal 3:


ros2 launch testbed_navigation localization.launch.py


Set the robot's initial pose in RViz using the 2D Pose Estimate tool.

### Step 7: Start navigation

In Terminal 4:


ros2 launch testbed_navigation navigation.launch.py


Use the 2D Goal Pose tool in RViz to send a navigation goal.

## 8. Testing and Results

The implementation was tested in the Testbed-T1.0.0 Gazebo simulation.

### Build verification

The workspace was successfully built using:


colcon build --symlink-install


The following packages were built:

- testbed_description
- testbed_bringup
- testbed_navigation
- testbed_gazebo

### Map loading check

Map loading in the Map Server was successful for the supplied map.

The size of the map is 405 x 400 cells with a resolution of 0.05 m/cell.

### Localization check

AMCL successfully subscribed to the map and was started by its Lifecycle Manager.

The initial robot pose was defined using RViz.

The transform between the map and odometry was seen after localization initialization.

### Navigation check
The following navigation servers were verified to be active:

- `/planner_server`
- `/controller_server`
- `/behavior_server`
- `/bt_navigator`

Lifecycle verification was performed using:


ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator


All four returned:

active [3]

The robot successfully received a navigation goal through RViz and reached the selected destination in Gazebo.

The global path and local trajectory were also visualized in RViz.

## 9. Challenges Faced and Improvements

### 9.1 Missing map installation rule

The old `testbed_bringup/CMakeLists.txt` would install the `launch` directory but not the `maps` directory.

The installation rule was added for both `launch` and `maps`.

This was validated by recompiling the package and ensuring that the YAML and PGM files appeared in the package share directory.

### 9.2 Hard-coded file paths

The first implementation had hard-coded paths which worked on the developer machine.

This was fixed by changing the path lookup to use `ament_index_python`.

The new map loading, localization, and navigation launch files worked successfully.

### 9.3 Loading of Behavior Tree plugins

At the time of configuration of navigation, some missing behavior tree plugin errors occurred.

The following plugin libraries have been added to the configuration `plugin_lib_names`:

- `nav2_remove_passed_goals_action_bt_node`
- `nav2_compute_path_through_poses_action_bt_node`

Navigation servers started working.

### 9.4 Requirement of Initial Pose

AMCL needs an initial pose estimate for localization initialization.

RobotModel was in Ok status only after 2D Pose Estimate was used in Rviz for providing an initial pose to amcl.

Initial pose is being given by hand through the 2D Pose Estimate in RViz.
### 9.5 Map Not Visible in Rviz

After executing the command for launching the testbed_bringup launch files, Gazebo and Rviz systems get opened, but the map does not appear in Rviz.

These were the actions performed:

1. Changed the Fixed Frame from `odom` to `map`

2. Added the map in display and configured its topic `/map`, Durability = `Transient_local`.

As a result, the map appeared in Rviz.

There is likely to be some lagging in the movement of Rviz robot and the robot in Gazebo, and sometimes Rviz robot used to be at very different positions as compared to the simulation.

## 10. Conclusion

I got to learn about the navigation, lifecycle management, planner_server, Map_server, controller etc and got a hands on eperience to navigate the robot in gazebo by manually creating the nav2 launch files to load map, start and estimate the robot position using amcl, and using planner, controller, behaviour servors and also about the BT navigator. 
It was a great part of learning to improving my ROS skill.
The robot was successfully localized and navigated to a selected goal in the Gazebo simulation. 


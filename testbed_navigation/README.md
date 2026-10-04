# Testbed Navigation

## Overview

This package implements a complete ROS 2 Navigation2 workflow for the Testbed-T1.0.0 robot using ROS 2 Humble, Gazebo 11 and RViz.

The navigation system was built manually instead of using a single `nav2_bringup` launch file.

## Package Structure

```text
testbed_navigation/
├── CMakeLists.txt
├── package.xml
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
└── launch/
    ├── map_loader.launch.py
    ├── localization.launch.py
    └── navigation.launch.py
```

## Navigation Architecture

The system is divided into three stages:

1. Map loading
2. Robot localization
3. Navigation

The main data flow is:

```text
Map Server
   ↓
/map

LaserScan + Odometry
   ↓
AMCL
   ↓
map → odom TF

Map + TF + LaserScan
   ↓
Global Costmap / Planner
   ↓
Local Costmap / Controller
   ↓
BT Navigator
   ↓
/cmd_vel
   ↓
Differential Drive Robot
```

## 1. Map Loading

The `map_loader.launch.py` launch file starts:

* `nav2_map_server`
* `nav2_lifecycle_manager`

The map is loaded from:

```text
testbed_bringup/maps/testbed_world.yaml
```

Launch:

# Testbed Navigation

## Overview

This package implements a complete ROS 2 Navigation2 workflow for the Testbed-T1.0.0 robot using ROS 2 Humble, Gazebo 11 and RViz.

The navigation system was built manually instead of using a single `nav2_bringup` launch file.

## Package Structure

```text
testbed_navigation/
├── CMakeLists.txt
├── package.xml
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
└── launch/
    ├── map_loader.launch.py
    ├── localization.launch.py
    └── navigation.launch.py
```

## Navigation Architecture

The system is divided into three stages:

1. Map loading
2. Robot localization
3. Navigation

The main data flow is:

```text
Map Server
   ↓
/map

LaserScan + Odometry
   ↓
AMCL
   ↓
map → odom TF

Map + TF + LaserScan
   ↓
Global Costmap / Planner
   ↓
Local Costmap / Controller
   ↓
BT Navigator
   ↓
/cmd_vel
   ↓
Differential Drive Robot
```

## 1. Map Loading

The `map_loader.launch.py` launch file starts:

* `nav2_map_server`
* `nav2_lifecycle_manager`

The map is loaded from:

```text
testbed_bringup/maps/testbed_world.yaml
```

Launch:

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

The map is published on:

```text
/map
```

## 2. Localization

The `localization.launch.py` launch file starts:

* AMCL
* lifecycle manager

AMCL uses:

* `/map`
* `/scan`
* `/odom`

and publishes the localization transform:

```text
map → odom
```

Launch:

```bash
ros2 launch testbed_navigation localization.launch.py
```

After starting localization, the robot initial pose is set in RViz using **2D Pose Estimate**.

## 3. Navigation

The `navigation.launch.py` launch file starts:

* Controller Server
* Planner Server
* Behavior Server
* BT Navigator
* lifecycle manager

The planner uses NavFn and the controller uses DWB.

Launch:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Navigation goals are sent using the **2D Goal Pose** tool in RViz.

## Configuration

### AMCL

`config/amcl_params.yaml` contains:

* AMCL particle limits
* laser model parameters
* scan and map topics
* odometry frame
* robot base frame
* map frame
* differential drive motion model

### Nav2

`config/nav2_params.yaml` contains configuration for:

* controller server
* DWB local controller
* planner server
* NavFn planner
* global costmap
* local costmap
* obstacle layer
* inflation layer
* behavior server
* BT navigator

## Testing

The navigation workflow was tested by:

1. Starting the Gazebo testbed.
2. Loading the provided map.
3. Starting AMCL localization.
4. Setting the initial robot pose in RViz.
5. Starting the Nav2 navigation stack.
6. Sending navigation goals in RViz.
7. Observing the robot plan and move toward the requested goal.

## Challenges and Fixes

### Starter package build issue

The `testbed_description` CMake file contained an invalid `ament_package` declaration. This was corrected to `ament_package()`.

### Map loading issue

The provided map YAML referenced an incorrect image path. The path was corrected to `testbed_world.pgm`.

### Installed map resources

The `testbed_bringup` package did not install its `maps` directory. The CMake install rule was updated so the map YAML and PGM files are available from the installed package.

### Robot spawn startup race

The robot spawn process could sometimes start before Gazebo was ready to provide the `/spawn_entity` service. Starting the spawn after Gazebo became ready resolved the issue.

### AMCL initial pose

AMCL requires an initial pose estimate before it can provide a valid global localization transform. The initial pose was supplied through RViz using **2D Pose Estimate**.

### BT Navigator plugin configuration

Some Behavior Tree nodes used by the Humble navigation tree were not initially included in the BT plugin list. The required plugins, including path-through-poses and remove-passed-goals plugins, were added to the navigation configuration.

## Result

The final system provides:

* Map loading
* AMCL localization
* TF-based localization
* Global path planning
* Local obstacle-aware control
* Behavior Tree navigation
* Goal-based robot navigation in RViz
```bash
ros2 launch testbed_navigation map_loader.launch.py
```

The map is published on:

```text
/map
```

## 2. Localization

The `localization.launch.py` launch file starts:

* AMCL
* lifecycle manager

AMCL uses:

* `/map`
* `/scan`
* `/odom`

and publishes the localization transform:

```text
map → odom
```

Launch:

```bash
ros2 launch testbed_navigation localization.launch.py
```

After starting localization, the robot initial pose is set in RViz using **2D Pose Estimate**.

## 3. Navigation

The `navigation.launch.py` launch file starts:

* Controller Server
* Planner Server
* Behavior Server
* BT Navigator
* lifecycle manager

The planner uses NavFn and the controller uses DWB.

Launch:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Navigation goals are sent using the **2D Goal Pose** tool in RViz.

## Configuration

### AMCL

`config/amcl_params.yaml` contains:

* AMCL particle limits
* laser model parameters
* scan and map topics
* odometry frame
* robot base frame
* map frame
* differential drive motion model

### Nav2

`config/nav2_params.yaml` contains configuration for:

* controller server
* DWB local controller
* planner server
* NavFn planner
* global costmap
* local costmap
* obstacle layer
* inflation layer
* behavior server
* BT navigator

## Testing

The navigation workflow was tested by:

1. Starting the Gazebo testbed.
2. Loading the provided map.
3. Starting AMCL localization.
4. Setting the initial robot pose in RViz.
5. Starting the Nav2 navigation stack.
6. Sending navigation goals in RViz.
7. Observing the robot plan and move toward the requested goal.

## Challenges and Fixes

### Starter package build issue

The `testbed_description` CMake file contained an invalid `ament_package` declaration. This was corrected to `ament_package()`.

### Map loading issue

The provided map YAML referenced an incorrect image path. The path was corrected to `testbed_world.pgm`.

### Installed map resources

The `testbed_bringup` package did not install its `maps` directory. The CMake install rule was updated so the map YAML and PGM files are available from the installed package.

### Robot spawn startup race

The robot spawn process could sometimes start before Gazebo was ready to provide the `/spawn_entity` service. Starting the spawn after Gazebo became ready resolved the issue.

### AMCL initial pose

AMCL requires an initial pose estimate before it can provide a valid global localization transform. The initial pose was supplied through RViz using **2D Pose Estimate**.

### BT Navigator plugin configuration

Some Behavior Tree nodes used by the Humble navigation tree were not initially included in the BT plugin list. The required plugins, including path-through-poses and remove-passed-goals plugins, were added to the navigation configuration.

## Result

The final system provides:

* Map loading
* AMCL localization
* TF-based localization
* Global path planning
* Local obstacle-aware control
* Behavior Tree navigation
* Goal-based robot navigation in RViz

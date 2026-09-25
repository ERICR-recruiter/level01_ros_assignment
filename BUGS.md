# Bugs Found in the Starter Code

I found 6 issues while setting up and testing the project. The Humble → Jazzy migration is documented separately in [`MIGRATION.md`](MIGRATION.md).

### 1. `ament_package` missing parentheses

**File:** `testbed_description/CMakeLists.txt`
`ament_package` was missing `()`, causing `colcon build` to fail.

**Fix:** Changed it to `ament_package()`.

### 2. Wrong map filename

**File:** `testbed_bringup/maps/testbed_world.yaml`
The YAML pointed to `wrong_path_testbed_world.pgm`, but the actual file was `testbed_world.pgm`.

**Fix:** Updated the `image:` path.

### 3. Maps not installed

**File:** `testbed_bringup/CMakeLists.txt`
The `maps` directory was not included in the install section, so the map could not be found from the installed package.

**Fix:** Added `maps` to the `install(DIRECTORY ...)` section.

### 4. Models not installed

**File:** `testbed_gazebo/CMakeLists.txt`
The `models` directory was not installed. It did not affect the current world, but the generated model path pointed to a missing directory.

**Fix:** Added `models` to the install section.

### 5. Lidar range too small

**File:** `testbed_description/urdf/testbed.gazebo`
The lidar range was limited to `1.5 m`, while the map is around `20 × 20 m`. The scan looked valid, but AMCL struggled to localize once the robot moved.

**Fix:** Increased the lidar range to `12.0 m` and adjusted the related AMCL/costmap parameters.


### 6. Missing package dependencies

**Files:** `testbed_description/package.xml`, `testbed_gazebo/package.xml`, `testbed_bringup/package.xml`
Several packages used by the launch files were not declared as dependencies. They worked on my machine because they were already installed.

**Fix:** Added the required dependencies to each `package.xml`.


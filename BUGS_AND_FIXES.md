# Bugs found in the starter code and how they were fixed

Found and fixed by reading the code only (no build/run pass was done —
see submission note at the bottom). Listed in order of how badly they'd
block the assignment.

## 1. `testbed_bringup/maps/testbed_world.yaml` — wrong image filename
**Bug:** `image: wrong_path_testbed_world.pgm`, but the actual file on
disk is `testbed_world.pgm`. `map_server` would fail to load the map at
all (deliverable step 4 — map loading — is dead on arrival).
**Fix:** Changed `image:` to `testbed_world.pgm`.

## 2. `testbed_description/urdf/testbed.gazebo` — malformed XML in the IMU plugin
**Bug:** Line 40 had a stray closing angle bracket:
`<initial_orientation_as_reference>false</initial_orientation_as_reference>>`
(two `>` at the end). This is invalid XML, so `xacro`/the URDF parser
would fail on the whole robot description, which means
`robot_state_publisher`, RViz and the Gazebo spawn would all fail.
**Fix:** Removed the extra `>`.

## 3. `testbed_description/urdf/testbed.gazebo` — lidar max range too short
**Bug:** The `head_hokuyo_sensor` ray sensor's `<range><max>` was `1.5`
(meters). The provided map (`testbed_world.pgm`) is 405x400 px at
0.05 m/px, i.e. roughly 20 m x 20 m. A 1.5 m max range means the laser
scan (and therefore AMCL and the Nav2 costmaps, which both consume
`/scan`) can only ever see ~1.5 m around the robot — nowhere near enough
to localize against or plan through most of the environment.
**Fix:** Increased `<range><max>` to `12.0` (typical of a real
low-cost planar lidar, e.g. RPLidar A1/A2) and matched that value in
`testbed_navigation`'s AMCL/costmap params.

## 4. `testbed_bringup/CMakeLists.txt` — `maps/` never installed
**Bug:** The package's `install(DIRECTORY ...)` call only listed
`launch`, so `colcon build` would never copy `maps/` into the install
space. Anything resolving the map via
`get_package_share_directory('testbed_bringup')` (including the new
`testbed_navigation/launch/map_loader.launch.py`) would fail to find
`testbed_world.yaml` after a normal build, even though it works from a
source checkout.
**Fix:** Added `maps` to the installed directories.

## 5. `testbed_gazebo/CMakeLists.txt` — `models/` never installed
**Bug:** Same issue as #4 but for `testbed_gazebo`: only `launch` and
`worlds` were installed, so the custom Gazebo models referenced by the
world files (`test_room`, `wooden_fence`, etc., used by
`testbed_playground.world`) would not exist in the install space, and
`GAZEBO_MODEL_PATH` (built from the installed package share dir in
`spawn_playground.launch.py`) would point at a `models/` folder that
was never installed.
**Fix:** Added `models` to the installed directories.

## 6. `testbed_gazebo/package.xml` — missing `gazebo_ros` dependency
**Bug:** `spawn_playground.launch.py` locates and includes
`gazebo_ros`'s `gazebo.launch.py` and the world plugins depend on
`gazebo_ros` at runtime, but the package never declared the dependency.
**Fix:** Added `<depend>gazebo_ros</depend>`.

---

## Submission note (time-boxed)

This pass was done under a hard time constraint and, per the request
under which it was done, **without building or running the workspace**
(no `colcon build`, no Gazebo/RViz/Nav2 launch was executed). Every fix
above was found by static reading of the XML/YAML/Python/URDF against
the corresponding Nav2/Gazebo/ROS2 docs and by cross-checking values
between files (e.g. the map's pixel dimensions vs. the lidar range, the
diff-drive plugin's frame names vs. the AMCL/Nav2 frame params).

That means:
- The bugs above are the ones that are visible from the code itself
  (broken paths, invalid XML, missing installs, inconsistent
  parameters). There could be additional *runtime-only* bugs (TF timing,
  plugin loading order, race conditions between Gazebo spawn and
  `spawn_entity.py`, etc.) that only show up once the stack is actually
  launched, which this pass could not catch.
- The new `testbed_navigation` package (map loading / localization /
  navigation launch files + AMCL/Nav2 param files) was written and
  cross-checked against the robot description and map, but **has not
  been build- or run-tested**. It should be treated as a first draft to
  validate with `colcon build` and a live Gazebo/RViz session before
  being considered final — see `testbed_navigation/README.md` for what
  to check first (initial pose, footprint, DWB gains).

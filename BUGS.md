# Bugs found in the starter code

Seven defects in the starter packages, in the order I hit them. Each one is
listed with the symptom that exposed it, the cause, and the change I made.

A couple of them (5 and 6) are not hard failures — they let the simulation
start and only bite later, once you try to localize. Those took the longest to
find, so I have written up how I cornered them rather than just quoting the
fix.

The Humble/Gazebo Classic to Jazzy/Gazebo Harmonic port is a separate piece of
work and is written up in [MIGRATION.md](MIGRATION.md). I have deliberately
kept it out of this file: none of it is a bug in the starter code, it is just
the cost of running on a newer distro.

---

## 1. `ament_package` called without parentheses

**File:** `testbed_description/CMakeLists.txt:23`

**Symptom:** `colcon build` fails immediately, and the error points at a line
that does not exist:

```
CMake Error at CMakeLists.txt:24:
  Parse error.  Expected "(", got newline with text "

  ".
```

**Cause:** the file ended with a bare `ament_package`. CMake reads a bare word
as the start of a command invocation, then walks forward looking for the
opening `(`, runs off the end of the file, and reports the failure at EOF —
which is line 24, one past the actual mistake on line 23.

Because `testbed_gazebo` declares `<depend>testbed_description</depend>`,
colcon skipped it entirely once the dependency failed to configure. So the
build summary showed two packages attempted out of three, which sent me
looking in the wrong place at first.

**Fix:**

```cmake
ament_package()
```

---

## 2. Map YAML points at a file that does not exist

**File:** `testbed_bringup/maps/testbed_world.yaml:1`

**Symptom:** `map_server` refuses to configure:

```
[map_io]: Loading image_file: .../maps/wrong_path_testbed_world.pgm
[ERROR] [map_server]: Caught exception in callback for transition 10
```

**Cause:** the `image:` key read `wrong_path_testbed_world.pgm`. The actual
image sitting next to it is `testbed_world.pgm`.

**Fix:**

```yaml
image: testbed_world.pgm
```

Kept relative rather than absolute — `nav2_map_server` resolves a relative
`image:` against the directory holding the YAML, so this stays correct
wherever the package is installed.

---

## 3. `maps/` is never installed

**File:** `testbed_bringup/CMakeLists.txt:27-32`

**Symptom:** with bug 2 fixed, the map still could not be found. Nothing under
`install/testbed_bringup/share/testbed_bringup/` except `launch`.

**Cause:** the `install(DIRECTORY ...)` block listed only `launch`. The map
lives in the source tree and never reaches the install space, so anything
resolving it through `get_package_share_directory('testbed_bringup')` — which
is what the assignment asks for — comes up empty.

**Fix:**

```cmake
install(
  DIRECTORY
    launch
    maps
  DESTINATION
    share/${PROJECT_NAME}/
)
```

---

## 4. `models/` is never installed either

**File:** `testbed_gazebo/CMakeLists.txt:28-34`

**Symptom:** no visible failure, which is why I nearly missed it.
`spawn_playground.launch.py` builds a model search path out of
`get_package_share_directory('testbed_gazebo') + '/models'` and exports it to
the simulator. That directory does not exist in the install space, so the
simulator was being handed a dead path on every run.

It happens not to matter today because `testbed_playground.world` defines
every model inline and never does `<include><uri>model://...`. It would matter
the moment anyone added one.

**Fix:** added `models` to the installed directories.

---

## 5. Lidar range is 1.5 m

**File:** `testbed_description/urdf/testbed.gazebo`, the lidar sensor's
`<range><max>`

**Symptom:** the simulation looked completely healthy. `/scan` published at
30 Hz, RViz drew a tidy little ring of points around the robot, TF was clean.
AMCL came up, accepted its initial pose, and then the particle cloud spread
out the moment the robot moved and never recovered.

**How I found it:** I checked the scan against the map it is supposed to
localize against:

```
$ ros2 topic echo /scan --once | grep range_max
range_max: 1.5
```

The map is 405 x 400 cells at 0.05 m/cell — roughly 20 m by 20 m, with rooms
several metres across. A 1.5 m sensor sees a blank circle of floor in the
middle of any of those rooms. Every particle in the filter scores identically,
because there is nothing in range to tell them apart, so the pose estimate is
driven by dead reckoning alone and drifts away.

**Cause:** an intentionally clipped `<max>`. The sensor is named
`head_hokuyo_sensor`; the real Hokuyo units this is modelled on run from 4 m
(URG-04LX) to 10-30 m (UST-10LX / UTM-30LX).

**Fix:** `<max>12.0</max>`, which is enough to see the far wall of any room in
this map while staying in the range a real Hokuyo would give you. The
matching consumers were set from the same number: `laser_max_range: 11.5` in
`amcl_params.yaml` (just under the sensor maximum, so max-range returns are not
treated as hits), and `obstacle_max_range: 8.0` / `raytrace_max_range: 10.0`
in the costmaps.

After the change, AMCL holds its pose over a 10 m cross-map run with zero
recovery behaviours triggered.

---

## 6. `use_sim_time: True` in a launch file with no simulator

**File:** `testbed_description/launch/testbed_rviz_barebones.launch.py`

**Symptom:** the "barebones" RViz view shows the robot's fixed structure, but
the wheels throw extrapolation errors and do not respond to the
`joint_state_publisher` sliders — which is the entire point of that launch
file.

**Cause:** the launch file starts `robot_state_publisher`,
`joint_state_publisher` and `rviz2` and nothing else, so nobody publishes
`/clock`. Two of the three were given `use_sim_time: True` and sit frozen at
t = 0; `joint_state_publisher` was left on wall time, because of the
commented-out block in that file noting it rejects the parameter.

That splits the TF tree across two clocks. Measured on a running instance:

```
/tf_static (robot_state_publisher, sim time)   stamp: sec: 0
/tf         (wheel joints, from joint_states)  stamp: sec: 1790323304
/joint_states (joint_state_publisher, wall)    stamp: sec: 1790323306
```

The static half is stamped 0 and the dynamic half is stamped ~1.79e9. RViz
runs at t = 0 with the rest, asks for `base_link -> left_wheel_1` at t = 0,
and gets a transform 56 years in its future.

I originally assumed this broke the view outright. It does not — static
transforms resolve fine at t = 0, which is why the robot still appears and why
it took a `ros2 topic echo` on both halves of the tree to see what was
actually wrong.

**Fix:** `use_sim_time: False` on all three nodes in that file, putting the
whole tree on one clock. The simulator-backed launches
(`robot_description.launch.py` and everything in `testbed_navigation`) still
run on sim time, where `/clock` genuinely exists.

---

## 7. Missing `package.xml` dependencies

**Files:** `testbed_description/package.xml`, `testbed_gazebo/package.xml`,
`testbed_bringup/package.xml`

**Symptom:** none on a machine that already has everything installed — which
is exactly the problem. The manifests only declared `ament_cmake`, `urdf` and
`rclpy`, while the launch files reach for `xacro`, `robot_state_publisher`,
`joint_state_publisher`, `rviz2` and the simulator bridge packages.

Everything resolved because those packages happen to be in the sourced
underlay. On a clean machine, `rosdep install --from-paths src` would install
none of them and the launch files would fail at runtime with
`package not found`.

**Fix:** declared what each package actually uses:

- `testbed_description`: `xacro`, `robot_state_publisher`,
  `joint_state_publisher`, `rviz2`
- `testbed_gazebo`: `ros_gz_sim`, `ros_gz_bridge`
- `testbed_bringup`: `testbed_description`, `testbed_gazebo`, `rviz2`

---

## Things that look like bugs but are not

Worth recording, because I spent time on each before deciding to leave it
alone.

**`spawn_playground.launch.py` declares a `world` argument and never passes it
on.** My first reading was that the playground world was silently never
loaded. It is not a bug: launch configurations propagate down into an
`IncludeLaunchDescription`, so the included Gazebo launch file picked up
`world` from the parent scope. I do pass it explicitly now, but only because
the Harmonic launch file takes `gz_args` rather than `world`.

**`testbed.trans` declares `<transmission>` blocks.** These target
`gazebo_ros_control`, which is not what drives the wheels — the diff-drive
plugin does. They are dead configuration rather than broken configuration, and
the URDF parser ignores them, so I left the file alone rather than widen the
diff. If this robot ever moves to `gz_ros2_control`, that is where the work
would start.

**`base_footprint` has a zero-size visual and no `<inertial>`.** It looks
wrong, but it is a normal massless root frame. The fixed joint to `base_link`
gets lumped during URDF-to-SDF conversion and the simulator never sees a
zero-mass body.

**Wheel geometry.** I checked `wheel_separation: 0.35` against the URDF rather
than trusting it: the wheel joints sit at y = +0.135241 and y = -0.210759, so
the true separation is 0.346 m. Wheel centres are 0.050004 m above
`base_link`, which sits at ground level, so the radius really is 0.05 m. Both
numbers in the plugin are correct.

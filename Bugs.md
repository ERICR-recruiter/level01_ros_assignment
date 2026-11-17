1. Fixed the CMake build failure by changing   ament_package   to   ament_package()   in   testbed_description/CMakeLists.txt.

2. Fixed missing installed map resources by adding the maps directory to the installation rule in     testbed_bringup/CMakeLists.txt.

3. Fixed the incorrect map image filename by changing    wrong_path_testbed_world.pgm    to    testbed_world.pgm   in  testbed_bringup/maps/testbed_world.yaml.

4. Fixed inconsistent clock settings by enabling use_sim_time for   robot_state_publisher    in testbed_description/launch/robot_description.launch.py.
  56. Removed an extra > after the IMU initial_orientation_as_reference parameter.
cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch config rviz behavior_trees
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/send_goal.py
    scripts/waypoint_benchmark.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(launch_testing_ament_cmake REQUIRED)
  add_launch_test(test/test_navigation_bringup.py TIMEOUT 180)
endif()

ament_package()

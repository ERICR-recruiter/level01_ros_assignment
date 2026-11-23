cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

find_package(ament_cmake REQUIRED)

# Launch files, parameter files, behavior trees and the RViz layout are all
# data: install them into share/testbed_navigation so that
# get_package_share_directory('testbed_navigation') can find them.
install(
  DIRECTORY
    launch
    config
    behavior_trees
    rviz
  DESTINATION
    share/${PROJECT_NAME}/
)

# Helper script(s) to send navigation goals from the command line:
#   ros2 run testbed_navigation send_goal.py
install(
  PROGRAMS
    scripts/send_goal.py
  DESTINATION
    lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

find_package(ament_cmake REQUIRED)

# Launch files, parameter files and the RViz layout are plain data:
# install them into share/testbed_navigation so they can be found with
# get_package_share_directory('testbed_navigation').
install(
  DIRECTORY
    behavior_trees
    config
    launch
    rviz
  DESTINATION
    share/${PROJECT_NAME}/
)

# Helper scripts (e.g. the NavigateToPose goal sender) -> lib/testbed_navigation
# so they can be started with `ros2 run testbed_navigation <script>`.
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

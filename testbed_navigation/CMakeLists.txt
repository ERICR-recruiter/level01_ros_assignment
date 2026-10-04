cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

find_package(ament_cmake REQUIRED)

# Launch files, parameter files and RViz configs are plain data: just install them
# so that `ros2 launch testbed_navigation <file>` can find them in share/.
install(
  DIRECTORY
    launch
    config
    rviz
  DESTINATION
    share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

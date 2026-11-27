cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

find_package(ament_cmake REQUIRED)

# Nothing to compile in this package - it's only launch files, parameter
# files, a BT xml and an rviz config. They just need to end up in share/.
install(
  DIRECTORY
    launch
    config
    rviz
    behavior_trees
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

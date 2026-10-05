cmake_minimum_required(VERSION 3.8)
project(testbed_gazebo)

find_package(ament_cmake REQUIRED)
find_package(testbed_description REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # Enable these checks after adding copyright and license headers.
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY launch worlds models
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

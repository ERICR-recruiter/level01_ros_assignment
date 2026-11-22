cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)

# Install directories for launch files, config/parameters, and rviz
install(
  DIRECTORY
    launch
    config
    rviz
  DESTINATION
    share/${PROJECT_NAME}/
)

# Install executable scripts if present in scripts/
file(GLOB SCRIPT_FILES "${CMAKE_CURRENT_SOURCE_DIR}/scripts/[!.]*")
if(SCRIPT_FILES)
  install(
    PROGRAMS ${SCRIPT_FILES}
    DESTINATION lib/${PROJECT_NAME}
  )
endif()

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

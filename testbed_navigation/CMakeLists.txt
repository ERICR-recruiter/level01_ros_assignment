cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)

# Include C++ headers directory
include_directories(
  include
)

# Install C++ header files
install(
  DIRECTORY include/
  DESTINATION include
)

# Install launch and params directories into package share
install(
  DIRECTORY launch config params
  DESTINATION share/${PROJECT_NAME}
)

# Enable testing setup
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED) # <--- Make sure this is present
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install config and launch directories into the share folder
# so they can be found by get_package_share_directory at runtime
install(
  DIRECTORY
    config
    launch
  DESTINATION
    share/${PROJECT_NAME}/
)

ament_package()

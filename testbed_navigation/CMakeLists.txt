cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    launch
    config
    rviz
  DESTINATION
    share/${PROJECT_NAME}
)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/scripts")
  install(
    DIRECTORY
      scripts/
    DESTINATION
      lib/${PROJECT_NAME}
    USE_SOURCE_PERMISSIONS
  )
endif()

ament_package()

cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

find_package(ament_cmake REQUIRED)

# Launch files, parameter files and the RViz view are data: install them to share/
install(
  DIRECTORY
    launch
    config
    rviz
  DESTINATION
    share/${PROJECT_NAME}/
)

# Helper scripts (e.g. sending a NavigateToPose goal from the terminal)
install(
  PROGRAMS
    scripts/send_goal.py
  DESTINATION
    lib/${PROJECT_NAME}
)

ament_package()

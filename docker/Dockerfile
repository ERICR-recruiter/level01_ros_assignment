FROM osrf/ros:humble-desktop-full

ENV DEBIAN_FRONTEND=noninteractive \
    RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    LIBGL_ALWAYS_SOFTWARE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-humble-navigation2 \
      ros-humble-gazebo-ros-pkgs \
      ros-humble-rmw-cyclonedds-cpp \
      ros-humble-xacro \
      ros-humble-robot-state-publisher \
      ros-humble-joint-state-publisher \
      ros-humble-tf2-tools \
      ros-humble-launch-testing-ament-cmake \
      python3-colcon-common-extensions \
      python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "[ -f /ws/install/setup.bash ] && source /ws/install/setup.bash" >> /root/.bashrc && \
    echo "source /usr/share/gazebo/setup.sh" >> /root/.bashrc

CMD ["bash"]

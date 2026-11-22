#!/usr/bin/env bash
set -euo pipefail
IMAGE=testbed_nav:humble
NAME=testbed_nav
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

xhost +local:docker >/dev/null 2>&1 || true

if docker ps -q -f name="^${NAME}$" | grep -q .; then
  exec docker exec -it "$NAME" bash
fi
docker rm -f "$NAME" >/dev/null 2>&1 || true

exec docker run -it --name "$NAME" \
  --net=host --ipc=host \
  -e DISPLAY="${DISPLAY:-:0}" -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --device /dev/dri \
  -v "$REPO_DIR":/ws/src/level01_ros_assignment \
  "$IMAGE" bash

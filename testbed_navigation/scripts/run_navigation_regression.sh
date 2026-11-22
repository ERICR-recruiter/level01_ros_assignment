#!/usr/bin/env bash
# Run only after Gazebo, Map Server, AMCL and Nav2 have been launched.
set -euo pipefail

ROUNDS="${1:-3}"
if ! [[ "$ROUNDS" =~ ^[1-9][0-9]*$ ]] || (( ROUNDS > 20 )); then
  echo 'Usage: run_navigation_regression.sh [number-of-round-trips, 1..20]' >&2
  exit 2
fi

for node in map_server amcl planner_server controller_server behavior_server bt_navigator; do
  state=''
  for attempt in 1 2 3; do
    state="$(timeout 15s ros2 lifecycle get "/$node" 2>&1 || true)"
    if [[ "$state" == 'active [3]' ]]; then
      break
    fi
    if (( attempt < 3 )); then
      echo "WARNING: $node lifecycle check attempt $attempt failed: $state" >&2
      sleep 1
    fi
  done
  if [[ "$state" != 'active [3]' ]]; then
    echo "ERROR: $node is not active or service is unresponsive: $state" >&2
    exit 2
  fi
done

LOG="${LOG:-/tmp/eric_navigation_regression_$(date +%Y%m%dT%H%M%S).log}"
echo "Recording test output to $LOG"
exec > >(tee -a "$LOG") 2>&1

for (( i=1; i<=ROUNDS; i++ )); do
  echo "========== Round $i/$ROUNDS =========="
  echo "GOAL 1: (1, 5, 0)"
  ros2 run testbed_navigation manual_navigation_test.py 1.0 5.0 --yaw 0.0
  ros2 run testbed_navigation report_pose_accuracy.py 1.0 5.0 --yaw 0.0
  echo "GOAL 2: (0, 5, 0)"
  ros2 run testbed_navigation manual_navigation_test.py 0.0 5.0 --yaw 0.0
  ros2 run testbed_navigation report_pose_accuracy.py 0.0 5.0 --yaw 0.0
done

echo "ALL $ROUNDS ROUND TRIPS PASSED both controller and pose checks"

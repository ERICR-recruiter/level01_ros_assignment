#!/usr/bin/env python3
"""
Semantic goal navigator for ERIC Robotics Testbed-T1.0.0.

Allows commanding the robot using semantic room names such as:
  ros2 run testbed_navigation move_to living_room
  ros2 run testbed_navigation move_to bathroom
  ros2 run testbed_navigation move_to "move to kitchen"
  ros2 run testbed_navigation move_to --list
"""

import argparse
import math
import os
import sys

from action_msgs.msg import GoalStatus
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
import yaml


def euler_to_quaternion(yaw: float, pitch: float = 0.0, roll: float = 0.0):
    """Convert euler angles to quaternion [x, y, z, w]."""
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return qx, qy, qz, qw


def load_waypoints():
    """Load semantic waypoints from YAML configuration."""
    # Check share directory first, then fallback to local repo config
    try:
        pkg_share = get_package_share_directory('testbed_navigation')
        config_path = os.path.join(pkg_share, 'config', 'waypoints.yaml')
    except Exception:
        config_path = None

    if not config_path or not os.path.exists(config_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, '..', 'config', 'waypoints.yaml')

    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('waypoints', {})


def resolve_location(user_input: str, waypoints: dict):
    """Match natural text or room name to a defined waypoint."""
    query = user_input.lower().strip()

    # Direct key match
    norm_key = query.replace(" ", "_")
    if norm_key in waypoints:
        return norm_key, waypoints[norm_key]

    # Clean filler words: 'move', 'go', 'navigate', 'to', 'the', 'please'
    filler_words = {"move", "go", "navigate", "drive", "to", "the", "please", "my", "at"}
    tokens = [t for t in query.replace("_", " ").split() if t not in filler_words]
    cleaned = " ".join(tokens)

    # Check aliases
    for key, info in waypoints.items():
        aliases = [a.lower() for a in info.get('aliases', [])]
        aliases.append(key.lower())
        aliases.append(key.lower().replace("_", " "))
        aliases.append(info.get('name', '').lower())

        if cleaned in aliases or query in aliases:
            return key, info

        for tok in tokens:
            if tok in aliases:
                return key, info

    return None, None


class RoomNavigator(Node):
    """ROS 2 node that sends NavigateToPose action goals by room name."""

    def __init__(self):
        super().__init__('room_navigator')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._goal_done = False
        self._goal_status = None

    def send_room_goal(self, room_key: str, room_info: dict):
        self.get_logger().info("Connecting to Nav2 '/navigate_to_pose' action server...")

        if not self._action_client.wait_for_server(timeout_sec=8.0):
            self.get_logger().error(
                "Action server '/navigate_to_pose' not available. "
                "Ensure testbed_navigation.launch.py is running!"
            )
            return False

        x = float(room_info['x'])
        y = float(room_info['y'])
        yaw = float(room_info.get('yaw', 0.0))
        qx, qy, qz, qw = euler_to_quaternion(yaw)

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = qx
        goal_msg.pose.pose.orientation.y = qy
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        room_name = room_info.get('name', room_key)
        print(f"\n>> Navigating to {room_name} (x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} rad)...")

        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Navigation goal was rejected by Nav2 bt_navigator.")
            return False

        print(">> Goal accepted by Nav2 stack. In motion...\n")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        status = result_future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            print(f"\n[SUCCESS] Robot has arrived at {room_name}!")
            return True
        else:
            print(f"\n[FAILED] Navigation stopped with status code: {status}")
            return False

    def _feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        dist = fb.distance_remaining
        eta = fb.estimated_time_remaining.sec
        print(f"\r   Distance remaining: {dist:5.2f} m | ETA: {eta:3d} s", end='', flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Command the Testbed robot to move to a room (e.g. living_room, bathroom)."
    )
    parser.add_argument(
        'destination',
        nargs='*',
        help="Room name or natural phrase (e.g. 'living_room', 'bathroom', 'move to kitchen')"
    )
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help="List all known rooms and their coordinates"
    )

    args = parser.parse_args()
    waypoints = load_waypoints()

    if args.list or not args.destination:
        print("\n=== AVAILABLE ROOM WAYPOINTS ===")
        print(f"{'ROOM ID':<15} {'NAME':<15} {'COORDINATES (x, y, yaw)':<25} {'ALIASES'}")
        print("-" * 75)
        for key, info in waypoints.items():
            coords = f"({info['x']:.1f}, {info['y']:.1f}, {info['yaw']:.2f})"
            aliases = ", ".join(info.get('aliases', []))
            print(f"{key:<15} {info['name']:<15} {coords:<25} {aliases}")
        print("\nUsage example:")
        print("  ros2 run testbed_navigation move_to living_room")
        print("  ros2 run testbed_navigation move_to bathroom")
        print("  ./move_to \"move to kitchen\"\n")
        if not args.destination:
            sys.exit(0)

    user_query = " ".join(args.destination)
    room_key, room_info = resolve_location(user_query, waypoints)

    if not room_info:
        print(f"\n[ERROR] Unknown destination: '{user_query}'")
        print("Run with --list to see available rooms.\n")
        sys.exit(1)

    rclpy.init()
    navigator = RoomNavigator()
    try:
        success = navigator.send_room_goal(room_key, room_info)
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
navigation_client.py — NavigateToPose action client for Testbed-T1.0.0

Sends a single (x, y, yaw) goal to the Nav2 NavigateToPose action server,
monitors feedback (distance remaining), and reports the final result.

Usage:
    ros2 run testbed_navigation navigation_client \
        --ros-args -p x:=2.0 -p y:=3.0 -p yaw:=0.0
"""
import math
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Quaternion


def yaw_to_quaternion(yaw: float) -> Quaternion:
    """Convert a yaw angle (radians) to a geometry_msgs Quaternion."""
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class NavigationClient(Node):
    """ROS 2 node that wraps the NavigateToPose action client."""

    def __init__(self):
        super().__init__('navigation_client')

        # Declare parameters with defaults
        self.declare_parameter('x', 0.0)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('yaw', 0.0)

        self._action_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )
        self._goal_handle = None

    # ------------------------------------------------------------------ #
    #  Public API                                                        #
    # ------------------------------------------------------------------ #

    def send_goal(self, x: float, y: float, yaw: float):
        """Build and send a NavigateToPose goal."""
        self.get_logger().info(
            f'Waiting for NavigateToPose action server …'
        )
        if not self._action_client.wait_for_server(timeout_sec=15.0):
            self.get_logger().error(
                'NavigateToPose action server not available after 15 s'
            )
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation = yaw_to_quaternion(yaw)

        self.get_logger().info(
            f'Sending goal → x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} rad'
        )

        send_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_cb
        )
        send_future.add_done_callback(self._goal_response_cb)

    # ------------------------------------------------------------------ #
    #  Callbacks                                                         #
    # ------------------------------------------------------------------ #

    def _goal_response_cb(self, future):
        """Called when the action server accepts or rejects the goal."""
        self._goal_handle = future.result()
        if not self._goal_handle.accepted:
            self.get_logger().warn('Goal REJECTED by server')
            return
        self.get_logger().info('Goal ACCEPTED — navigating …')
        result_future = self._goal_handle.get_result_async()
        result_future.add_done_callback(self._result_cb)

    def _feedback_cb(self, feedback_msg):
        """Called periodically while the robot is navigating."""
        fb = feedback_msg.feedback
        dist = fb.distance_remaining
        self.get_logger().info(f'Distance remaining: {dist:.2f} m')

    def _result_cb(self, future):
        """Called when navigation finishes (success, failure, or cancel)."""
        result = future.result()
        status = result.status

        status_map = {
            2: 'ACTIVE',
            4: 'SUCCEEDED',
            5: 'CANCELED',
            6: 'ABORTED',
        }
        label = status_map.get(status, f'UNKNOWN ({status})')

        if status == 4:
            self.get_logger().info(f'Navigation result: {label} ✓')
        else:
            self.get_logger().warn(f'Navigation result: {label}')

        # Shut down after the goal completes
        rclpy.shutdown()

    def cancel_goal(self):
        """Cancel an in-progress goal."""
        if self._goal_handle is not None:
            self.get_logger().info('Cancelling navigation goal …')
            self._goal_handle.cancel_goal_async()


# ---------------------------------------------------------------------- #
#  Entry point                                                           #
# ---------------------------------------------------------------------- #

def main(args=None):
    rclpy.init(args=args)
    node = NavigationClient()

    x = node.get_parameter('x').get_parameter_value().double_value
    y = node.get_parameter('y').get_parameter_value().double_value
    yaw = node.get_parameter('yaw').get_parameter_value().double_value

    node.send_goal(x, y, yaw)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.cancel_goal()
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
navigation_monitor.py — ROS 2 topic / TF / action-server health monitor

Reports live status of every interface the Nav2 stack depends on:
  /clock  /map  /scan  /odom  /imu  /cmd_vel  /tf  /tf_static
  NavigateToPose action server availability
  map → odom → base_footprint TF chain

Usage:
    ros2 run testbed_navigation navigation_monitor
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry, OccupancyGrid
from geometry_msgs.msg import Twist
from rosgraph_msgs.msg import Clock
from tf2_msgs.msg import TFMessage
from nav2_msgs.action import NavigateToPose

import time


class NavigationMonitor(Node):
    """Periodically reports topic health and TF status."""

    TOPICS = {
        '/clock':     Clock,
        '/map':       OccupancyGrid,
        '/scan':      LaserScan,
        '/odom':      Odometry,
        '/imu':       Imu,
        '/cmd_vel':   Twist,
    }

    def __init__(self):
        super().__init__('navigation_monitor')
        self._received = {}     # topic → bool
        self._msg_count = {}    # topic → int
        self._subs = []

        # Subscribe to each topic
        for topic, msg_type in self.TOPICS.items():
            self._received[topic] = False
            self._msg_count[topic] = 0

            # /map uses transient-local
            if topic == '/map':
                qos = QoSProfile(
                    depth=1,
                    durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE,
                )
            else:
                qos = 10

            sub = self.create_subscription(
                msg_type, topic,
                lambda msg, t=topic: self._topic_cb(t),
                qos,
            )
            self._subs.append(sub)

        # TF subscriptions
        self._tf_frames = set()
        self.create_subscription(TFMessage, '/tf', self._tf_cb, 10)
        self.create_subscription(
            TFMessage, '/tf_static',
            self._tf_cb,
            QoSProfile(
                depth=10,
                durability=DurabilityPolicy.TRANSIENT_LOCAL,
                reliability=ReliabilityPolicy.RELIABLE,
            ),
        )

        # Action client for availability check
        self._nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )

        # Print report every 5 s
        self.create_timer(5.0, self._report)

    # ------------------------------------------------------------------ #

    def _topic_cb(self, topic):
        self._received[topic] = True
        self._msg_count[topic] += 1

    def _tf_cb(self, msg):
        for t in msg.transforms:
            self._tf_frames.add(t.header.frame_id)
            self._tf_frames.add(t.child_frame_id)

    # ------------------------------------------------------------------ #

    def _report(self):
        self.get_logger().info('──── Navigation Health Report ────')

        # Topics
        for topic in self.TOPICS:
            ok = self._received[topic]
            cnt = self._msg_count[topic]
            status = f'✓ receiving ({cnt} msgs)' if ok else '✗ no data'
            self.get_logger().info(f'  {topic:20s} {status}')

        # TF frames
        expected = {'map', 'odom', 'base_footprint', 'base_link',
                    'lidar_link_1', 'imu_link_1'}
        present = expected & self._tf_frames
        missing = expected - self._tf_frames
        self.get_logger().info(f'  TF frames present : {sorted(present)}')
        if missing:
            self.get_logger().warn(f'  TF frames MISSING : {sorted(missing)}')

        # Action server
        nav_ready = self._nav_client.server_is_ready()
        nav_label = '✓ ready' if nav_ready else '✗ not available'
        self.get_logger().info(f'  navigate_to_pose   {nav_label}')

        self.get_logger().info('──────────────────────────────────')


# ---------------------------------------------------------------------- #

def main(args=None):
    rclpy.init(args=args)
    node = NavigationMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

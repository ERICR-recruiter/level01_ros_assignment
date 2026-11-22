#!/usr/bin/env python3
"""Runs the robot through a few waypoints and logs time / error for each one.
/odom from gazebo is in the world frame so I use it as ground truth."""
import argparse
import math
import time

import rclpy
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.qos import DurabilityPolicy, QoSProfile

TOUR = [
    ('upper-right corner', 6.0, 7.5, 0.0),
    ('upper-left via inner gap', -6.5, 1.5, math.pi),
    ('through doorway (lower room)', 3.8, -2.0, -math.pi / 2),
    ('lower-middle', -1.0, -3.0, math.pi),
    ('back to spawn', 0.0, 5.0, 0.0),
]


def yaw_of(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def ang_diff(a, b):
    return abs(math.atan2(math.sin(a - b), math.cos(a - b)))


class Tracker:

    def __init__(self, node):
        self.odom = None
        self.amcl = None
        self.distance = 0.0
        self._last = None
        node.create_subscription(Odometry, 'odom', self._on_odom, 20)
        node.create_subscription(
            PoseWithCovarianceStamped, 'amcl_pose', self._on_amcl,
            QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))

    def _on_odom(self, msg):
        p = msg.pose.pose
        if self._last is not None:
            self.distance += math.hypot(p.position.x - self._last.position.x,
                                        p.position.y - self._last.position.y)
        self._last = p
        self.odom = p

    def _on_amcl(self, msg):
        self.amcl = msg.pose.pose

    def localization_error(self):
        if self.odom is None or self.amcl is None:
            return float('nan')
        return math.hypot(self.odom.position.x - self.amcl.position.x,
                          self.odom.position.y - self.amcl.position.y)


def make_pose(nav, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--laps', type=int, default=1)
    parser.add_argument('--timeout', type=float, default=120.0, help='per-goal timeout [s]')
    parser.add_argument('--out', default='benchmark_results.md')
    args, ros_args = parser.parse_known_args()

    rclpy.init(args=ros_args)
    nav = BasicNavigator()
    tracker = Tracker(nav)
    nav.waitUntilNav2Active(localizer='amcl')

    rows = []
    for lap in range(1, args.laps + 1):
        for name, x, y, yaw in TOUR:
            start_dist = tracker.distance
            t0 = time.monotonic()
            nav.goToPose(make_pose(nav, x, y, yaw))
            while not nav.isTaskComplete():
                if time.monotonic() - t0 > args.timeout:
                    nav.cancelTask()
            dt = time.monotonic() - t0
            result = nav.getResult()
            for _ in range(10):
                rclpy.spin_once(nav, timeout_sec=0.05)
            p = tracker.odom
            pos_err = math.hypot(p.position.x - x, p.position.y - y) if p else float('nan')
            yaw_err = math.degrees(ang_diff(yaw_of(p.orientation), yaw)) if p else float('nan')
            row = dict(lap=lap, name=name, goal=f'({x:.1f}, {y:.1f})',
                       ok=result == TaskResult.SUCCEEDED, time=dt,
                       dist=tracker.distance - start_dist,
                       pos_err=pos_err, yaw_err=yaw_err, loc_err=tracker.localization_error())
            rows.append(row)
            nav.get_logger().info(
                f"[lap {lap}] {name}: {'SUCCEEDED' if row['ok'] else result} "
                f"in {dt:.1f}s, driven {row['dist']:.2f} m, goal err {pos_err:.3f} m / "
                f"{yaw_err:.1f} deg, AMCL err {row['loc_err']:.3f} m")

    ok = sum(r['ok'] for r in rows)
    lines = [
        '| Lap | Goal | Target (x, y) | Result | Time [s] | Driven [m] '
        '| Goal error [m] | Yaw error [deg] | AMCL error [m] |',
        '|---|---|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        lines.append(
            f"| {r['lap']} | {r['name']} | {r['goal']} | {'ok' if r['ok'] else 'FAIL'} "
            f"| {r['time']:.1f} | {r['dist']:.2f} | {r['pos_err']:.3f} | {r['yaw_err']:.1f} "
            f"| {r['loc_err']:.3f} |")
    lines.append('')
    lines.append(f'success {ok}/{len(rows)}, driven '
                 f"{sum(r['dist'] for r in rows):.1f} m, max amcl error "
                 f"{max(r['loc_err'] for r in rows):.3f} m")
    with open(args.out, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    nav.get_logger().info(f'Results written to {args.out}')

    nav.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

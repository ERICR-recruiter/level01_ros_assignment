#!/usr/bin/env python3
"""Validate navigation accuracy against map-frame TF and Gazebo ground truth.

Unlike /amcl_pose, the map -> base_footprint transform can be read after the
robot stops. AMCL may not publish new pose messages while stationary, so a
newly created /amcl_pose subscriber is not a reliable end-of-run test.

The Gazebo-world versus map-frame comparison assumes the simulation world and
occupancy map have been registered to the same coordinates.
"""

import argparse
import math
import subprocess
import sys
import time

import rclpy
from rclpy.parameter import Parameter
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener


def wrap_angle(value):
    return math.atan2(math.sin(value), math.cos(value))


def yaw_from_quaternion(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z),
    )


def calculate_error(x, y, yaw, args):
    return math.hypot(x - args.x, y - args.y), abs(wrap_angle(yaw - args.yaw))


def get_map_frame_pose(node, timeout):
    """Look up the latest TF pose, allowing listener callbacks to run."""
    buffer = Buffer()
    listener = TransformListener(buffer, node, spin_thread=False)
    deadline = time.monotonic() + timeout
    last_error = None

    # Keep the listener alive for the duration of these callbacks.
    while rclpy.ok() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.20)
        try:
            transform = buffer.lookup_transform('map', 'base_footprint', Time())
        except TransformException as exc:
            last_error = exc
            continue
        translation = transform.transform.translation
        rotation = transform.transform.rotation
        return translation.x, translation.y, yaw_from_quaternion(rotation)

    raise RuntimeError(
        'No map -> base_footprint TF available. Confirm AMCL, /tf, /odom '
        'and robot_state_publisher are running. Last TF error: '
        f'{last_error}'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('x', type=float, help='Target X in the occupancy-map frame')
    parser.add_argument('y', type=float, help='Target Y in the occupancy-map frame')
    parser.add_argument('--yaw', type=float, default=0.0, help='Target yaw in radians')
    parser.add_argument('--model', default='testbed', help='Gazebo model name')
    parser.add_argument('--timeout', type=float, default=12.0)
    parser.add_argument('--xy-tolerance', type=float, default=0.05)
    parser.add_argument('--yaw-tolerance', type=float, default=0.10)
    parser.add_argument('--physical-xy-tolerance', type=float, default=0.10,
                        help='Separate Gazebo ground-truth threshold; default 10 cm')
    args = parser.parse_args()
    if min(args.timeout, args.xy_tolerance, args.yaw_tolerance,
           args.physical_xy_tolerance) <= 0:
        parser.error('Timeout and tolerances must be positive')

    try:
        output = subprocess.run(
            ['gz', 'model', '-m', args.model, '-p'],
            check=True, text=True, capture_output=True, timeout=args.timeout,
        ).stdout.strip()
        gz_x, gz_y, _gz_z, gz_roll, gz_pitch, gz_yaw = map(float, output.split()[:6])
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
            ValueError) as exc:
        print(f'ERROR: cannot get Gazebo model pose: {exc}', file=sys.stderr)
        return 2

    rclpy.init()
    node = rclpy.create_node(
        'report_pose_accuracy',
        parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)],
    )
    try:
        try:
            est_x, est_y, est_yaw = get_map_frame_pose(node, args.timeout)
        except RuntimeError as exc:
            print(f'ERROR: {exc}', file=sys.stderr)
            return 2
    finally:
        node.destroy_node()
        rclpy.shutdown()

    est_xy_error, est_yaw_error = calculate_error(est_x, est_y, est_yaw, args)
    true_xy_error, true_yaw_error = calculate_error(gz_x, gz_y, gz_yaw, args)
    disagreement = math.hypot(est_x - gz_x, est_y - gz_y)

    print('Requested goal:  x={:.3f}  y={:.3f}  yaw={:.3f} rad'.format(
        args.x, args.y, args.yaw))
    print('Gazebo world:    x={:.3f}  y={:.3f}  yaw={:.3f} rad'.format(
        gz_x, gz_y, gz_yaw))
    print('Nav2 map TF:     x={:.3f}  y={:.3f}  yaw={:.3f} rad'.format(
        est_x, est_y, est_yaw))
    print('Estimated goal error: XY={:.3f} m, yaw={:.3f} rad'.format(
        est_xy_error, est_yaw_error))
    print('Physical goal error:  XY={:.3f} m, yaw={:.3f} rad'.format(
        true_xy_error, true_yaw_error))
    print('Map TF/Gazebo XY disagreement: {:.3f} m'.format(disagreement))

    estimated_ok = est_xy_error <= args.xy_tolerance and est_yaw_error <= args.yaw_tolerance
    physical_ok = true_xy_error <= args.physical_xy_tolerance and true_yaw_error <= args.yaw_tolerance
    if estimated_ok and physical_ok:
        print('POSE VALIDATION PASSED')
        return 0
    print('POSE VALIDATION FAILED (see estimated/physical errors above)')
    return 1


if __name__ == '__main__':
    sys.exit(main())

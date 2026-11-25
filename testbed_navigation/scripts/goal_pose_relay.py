#!/usr/bin/env python3
"""Transforms incoming /goal_pose messages into the global 'map' frame once on receipt.

Prevents TF2 extrapolation-into-the-past errors in planner_server when RViz sends
2D Goal Pose messages in 'odom' frame (e.g., when RViz Fixed Frame is left on 'odom')
and navigation takes longer than the 10-second TF buffer history.
"""

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time
import tf2_ros
from geometry_msgs.msg import PoseStamped


def quat_mul(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return (
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    )


def rotate_vec_by_quat(v, q):
    vx, vy, vz = v
    qx, qy, qz, qw = q
    p = (vx, vy, vz, 0.0)
    q_conj = (-qx, -qy, -qz, qw)
    rx, ry, rz, _ = quat_mul(quat_mul(q, p), q_conj)
    return (rx, ry, rz)


class GoalPoseRelay(Node):
    def __init__(self):
        super().__init__('goal_pose_relay')
        self.declare_parameter('target_frame', 'map')
        self.target_frame = self.get_parameter('target_frame').get_parameter_value().string_value

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.pub = self.create_publisher(PoseStamped, 'goal_pose_map', 10)
        self.sub = self.create_subscription(PoseStamped, 'goal_pose', self.goal_cb, 10)

    def goal_cb(self, msg: PoseStamped):
        src_frame = msg.header.frame_id.strip() if msg.header.frame_id else self.target_frame
        if src_frame == self.target_frame or src_frame == '/' + self.target_frame:
            out = PoseStamped()
            out.header.frame_id = self.target_frame
            out.header.stamp = msg.header.stamp
            out.pose = msg.pose
            self.pub.publish(out)
            return

        try:
            tf = self.tf_buffer.lookup_transform(
                self.target_frame,
                src_frame,
                Time(),
                timeout=Duration(seconds=0.5),
            )
            tr = tf.transform.translation
            rot = tf.transform.rotation
            q_tf = (rot.x, rot.y, rot.z, rot.w)

            pos = (msg.pose.position.x, msg.pose.position.y, msg.pose.position.z)
            rx, ry, rz = rotate_vec_by_quat(pos, q_tf)

            q_pose = (
                msg.pose.orientation.x,
                msg.pose.orientation.y,
                msg.pose.orientation.z,
                msg.pose.orientation.w,
            )
            nx, ny, nz, nw = quat_mul(q_tf, q_pose)

            out = PoseStamped()
            out.header.frame_id = self.target_frame
            out.header.stamp = self.get_clock().now().to_msg()
            out.pose.position.x = tr.x + rx
            out.pose.position.y = tr.y + ry
            out.pose.position.z = tr.z + rz
            out.pose.orientation.x = nx
            out.pose.orientation.y = ny
            out.pose.orientation.z = nz
            out.pose.orientation.w = nw
            self.pub.publish(out)
            self.get_logger().info(
                f'Converted goal from [{src_frame}] to [{self.target_frame}]: '
                f'({out.pose.position.x:.2f}, {out.pose.position.y:.2f})'
            )
        except Exception as exc:
            self.get_logger().warn(
                f'Could not transform goal from [{src_frame}] to [{self.target_frame}]: {exc}. Forwarding original.'
            )
            self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = GoalPoseRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

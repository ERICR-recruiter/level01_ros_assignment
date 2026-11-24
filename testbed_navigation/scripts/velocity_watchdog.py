#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityWatchdog(Node):
    def __init__(self):
        super().__init__('velocity_watchdog')
        self.sub = self.create_subscription(Twist, '/cmd_vel_nav', self.cb, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.max_lin = 0.45
        self.max_ang = 0.70
        self.get_logger().info('VelocityWatchdog active: relaying /cmd_vel_nav -> /cmd_vel')

    def cb(self, msg: Twist):
        out = Twist()
        out.linear.x = max(-0.15, min(self.max_lin, msg.linear.x))
        out.angular.z = max(-self.max_ang, min(self.max_ang, msg.angular.z))
        self.pub.publish(out)

def main():
    rclpy.init()
    node = VelocityWatchdog()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

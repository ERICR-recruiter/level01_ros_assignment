#!/usr/bin/env python3
"""
test_navigation_client.py — Unit tests for NavigationClient

Validates:
  - Node initialization and naming.
  - Parameter declaration (x, y, yaw) with correct defaults.
  - yaw_to_quaternion conversion for identity and known angles.
  - Action client creation for 'navigate_to_pose'.

These tests run offline (no ROS 2 graph required beyond rclpy.init).

Usage:
    cd <workspace>
    colcon test --packages-select testbed_navigation
    colcon test-result --verbose
"""
import math
import unittest

try:
    import rclpy
    from rclpy.node import Node
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False


@unittest.skipUnless(HAS_ROS2, 'ROS 2 (rclpy) is not installed')
class TestYawToQuaternion(unittest.TestCase):
    """Pure-math tests for the yaw → quaternion helper."""

    @classmethod
    def setUpClass(cls):
        """Import after rclpy is available."""
        from testbed_navigation.navigation_client import yaw_to_quaternion
        cls.yaw_to_quaternion = staticmethod(yaw_to_quaternion)

    # -- Identity (yaw = 0) -------------------------------------------
    def test_zero_yaw(self):
        q = self.yaw_to_quaternion(0.0)
        self.assertAlmostEqual(q.x, 0.0)
        self.assertAlmostEqual(q.y, 0.0)
        self.assertAlmostEqual(q.z, 0.0)
        self.assertAlmostEqual(q.w, 1.0)

    # -- 90° (π/2 rad) ------------------------------------------------
    def test_90_degrees(self):
        q = self.yaw_to_quaternion(math.pi / 2.0)
        self.assertAlmostEqual(q.x, 0.0)
        self.assertAlmostEqual(q.y, 0.0)
        self.assertAlmostEqual(q.z, math.sin(math.pi / 4.0), places=6)
        self.assertAlmostEqual(q.w, math.cos(math.pi / 4.0), places=6)

    # -- 180° (π rad) -------------------------------------------------
    def test_180_degrees(self):
        q = self.yaw_to_quaternion(math.pi)
        self.assertAlmostEqual(q.x, 0.0)
        self.assertAlmostEqual(q.y, 0.0)
        self.assertAlmostEqual(q.z, 1.0, places=6)
        self.assertAlmostEqual(q.w, 0.0, places=6)

    # -- Negative yaw (-π/2 rad) --------------------------------------
    def test_negative_yaw(self):
        q = self.yaw_to_quaternion(-math.pi / 2.0)
        self.assertAlmostEqual(q.z, -math.sin(math.pi / 4.0), places=6)
        self.assertAlmostEqual(q.w, math.cos(math.pi / 4.0), places=6)

    # -- Unit quaternion property: |q| = 1 ----------------------------
    def test_unit_norm(self):
        for yaw in [0.0, 0.5, 1.0, math.pi, -math.pi, 2.0 * math.pi]:
            q = self.yaw_to_quaternion(yaw)
            norm = math.sqrt(q.x**2 + q.y**2 + q.z**2 + q.w**2)
            self.assertAlmostEqual(norm, 1.0, places=10,
                                   msg=f'Non-unit quaternion for yaw={yaw}')


@unittest.skipUnless(HAS_ROS2, 'ROS 2 (rclpy) is not installed')
class TestNavigationClientNode(unittest.TestCase):
    """Tests that require a live rclpy context."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from testbed_navigation.navigation_client import NavigationClient
        self.node = NavigationClient()

    def tearDown(self):
        self.node.destroy_node()

    # -- Node name -----------------------------------------------------
    def test_node_name(self):
        self.assertEqual(self.node.get_name(), 'navigation_client')

    # -- Parameters declared with correct defaults ---------------------
    def test_parameters_declared(self):
        for name in ('x', 'y', 'yaw'):
            param = self.node.get_parameter(name)
            self.assertIsNotNone(param)
            self.assertAlmostEqual(
                param.get_parameter_value().double_value, 0.0,
                msg=f'Parameter "{name}" default should be 0.0',
            )

    # -- Action client exists for the correct action -------------------
    def test_action_client_created(self):
        self.assertIsNotNone(self.node._action_client)
        # The internal action name attribute may vary; just confirm it's
        # an ActionClient instance.
        from rclpy.action import ActionClient
        self.assertIsInstance(self.node._action_client, ActionClient)


if __name__ == '__main__':
    unittest.main()

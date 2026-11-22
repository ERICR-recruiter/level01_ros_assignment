"""Starts the sim + nav stack headless and checks all nav2 nodes become active."""
import os
import time
import unittest

import launch
import launch_testing
import launch_testing.actions
import pytest
import rclpy
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from lifecycle_msgs.msg import State
from lifecycle_msgs.srv import GetState

LIFECYCLE_NODES = [
    'map_server', 'amcl',
    'controller_server', 'planner_server', 'behavior_server', 'bt_navigator',
    'waypoint_follower', 'velocity_smoother', 'collision_monitor',
]
TIMEOUT_S = 150.0


@pytest.mark.launch_test
def generate_test_description():
    demo = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('testbed_navigation'),
            'launch', 'testbed_navigation.launch.py')),
        launch_arguments={'gui': 'false', 'use_rviz': 'false'}.items())
    return launch.LaunchDescription([demo, launch_testing.actions.ReadyToTest()])


class TestNavigationBringup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = rclpy.create_node('nav_smoke_test')

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def _state(self, name):
        client = self.node.create_client(GetState, f'/{name}/get_state')
        try:
            if not client.wait_for_service(timeout_sec=1.0):
                return None
            future = client.call_async(GetState.Request())
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=2.0)
            return future.result().current_state.id if future.result() else None
        finally:
            self.node.destroy_client(client)

    def test_all_lifecycle_nodes_active(self):
        deadline = time.monotonic() + TIMEOUT_S
        pending = set(LIFECYCLE_NODES)
        while pending and time.monotonic() < deadline:
            for name in list(pending):
                if self._state(name) == State.PRIMARY_STATE_ACTIVE:
                    pending.discard(name)
            time.sleep(1.0)
        self.assertFalse(pending, f'nodes not ACTIVE after {TIMEOUT_S}s: {sorted(pending)}')

    def test_no_nav2_bringup_used(self):
        share = get_package_share_directory('testbed_navigation')
        for root, _, files in os.walk(os.path.join(share, 'launch')):
            for f in (f for f in files if f.endswith('.py')):
                with open(os.path.join(root, f)) as fh:
                    src = fh.read()
                self.assertNotIn("'nav2_bringup'", src, f)
                self.assertNotIn('"nav2_bringup"', src, f)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):

    def test_exit_codes(self, proc_info):
        for info in proc_info:
            self.assertNotIn(info.returncode, [-11, 134, 139], f'{info.process_name} crashed')

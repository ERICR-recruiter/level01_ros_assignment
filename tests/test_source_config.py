"""Offline structural smoke tests for the ERIC Testbed navigation exercise."""

import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]


class StaticConfigurationTests(unittest.TestCase):
    def test_sdf_room_aligned_with_map(self):
        world = ElementTree.parse(
            ROOT / 'testbed_gazebo/worlds/testbed_playground.world'
        )
        rooms = world.findall('.//world/model[@name="test_room"]')
        self.assertEqual(len(rooms), 1)
        pose = list(map(float, rooms[0].findtext('pose').split()))
        self.assertLess(max(abs(item) for item in pose), 1e-6)
        # Saved Gazebo states can override the model pose at startup.
        self.assertIsNone(world.find('world/state'),
                          'The world must not contain a stale saved simulation state')

    def test_gazebo_urdf_xml_syntax(self):
        ElementTree.parse(ROOT / 'testbed_description/urdf/testbed.gazebo')
        ElementTree.parse(ROOT / 'testbed_description/urdf/testbed.xacro')
        self.assertNotIn('libgazebo_ros_control.so', (
            ROOT / 'testbed_description/urdf/testbed.gazebo'
        ).read_text())

    @unittest.skipIf(yaml is None, 'Install python3-yaml for YAML tests')
    def test_amcl_and_sensor_ranges_match(self):
        config = yaml.safe_load((ROOT / 'testbed_navigation/config/amcl_params.yaml').read_text())
        distance = config['amcl']['ros__parameters']['laser_max_range']
        gazebo = ElementTree.parse(ROOT / 'testbed_description/urdf/testbed.gazebo')
        lidar_range = float(gazebo.findtext('.//sensor[@type="ray"]/ray/range/max'))
        self.assertEqual(float(distance), lidar_range)

    @unittest.skipIf(yaml is None, 'Install python3-yaml for YAML tests')
    def test_nav2_consistency(self):
        config = yaml.safe_load((ROOT / 'testbed_navigation/config/nav2_params.yaml').read_text())
        ctrl = config['controller_server']['ros__parameters']
        self.assertEqual(ctrl['progress_checker']['plugin'],
                         'nav2_controller::PoseProgressChecker')
        self.assertFalse(ctrl['general_goal_checker']['stateful'])
        self.assertEqual(ctrl['general_goal_checker']['xy_goal_tolerance'], 0.05)
        self.assertTrue(ctrl['FollowPath']['plugin'].endswith('RegulatedPurePursuitController'))
        for section in ('bt_navigator', 'behavior_server'):
            self.assertEqual(config[section]['ros__parameters']['robot_base_frame'],
                             'base_footprint')
        for section in ('local_costmap', 'global_costmap'):
            self.assertEqual(config[section][section]['ros__parameters']['robot_base_frame'],
                             'base_footprint')

    def test_required_package_files(self):
        for rel in ('testbed_navigation/launch/map_loader.launch.py',
                    'testbed_navigation/launch/localization.launch.py',
                    'testbed_navigation/launch/navigation.launch.py',
                    'testbed_navigation/scripts/manual_navigation_test.py',
                    'testbed_navigation/scripts/report_pose_accuracy.py',
                    'bugs_fixed.txt'):
            self.assertTrue((ROOT / rel).is_file(), rel)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""
test_navigation_config.py — Configuration validation tests

Validates that every YAML config, the BT XML, and package.xml are
syntactically correct and contain the keys and values that the
navigation stack depends on.

These tests are purely file-based and do not require a running
ROS 2 graph.

Usage:
    cd <workspace>
    colcon test --packages-select testbed_navigation
    colcon test-result --verbose
"""
import os
import unittest
import xml.etree.ElementTree as ET

import yaml


def _pkg_root() -> str:
    """Return the testbed_navigation package root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestMapServerParams(unittest.TestCase):
    """Validate config/map_server_params.yaml."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(_pkg_root(), 'config', 'map_server_params.yaml')
        with open(path, 'r') as f:
            cls.data = yaml.safe_load(f)

    def test_top_level_key(self):
        self.assertIn('map_server', self.data)

    def test_use_sim_time(self):
        params = self.data['map_server']['ros__parameters']
        self.assertTrue(params['use_sim_time'])

    def test_frame_id(self):
        params = self.data['map_server']['ros__parameters']
        self.assertEqual(params['frame_id'], 'map')

    def test_topic_name(self):
        params = self.data['map_server']['ros__parameters']
        self.assertEqual(params['topic_name'], 'map')


class TestAmclParams(unittest.TestCase):
    """Validate config/amcl_params.yaml."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(_pkg_root(), 'config', 'amcl_params.yaml')
        with open(path, 'r') as f:
            cls.data = yaml.safe_load(f)

    def test_top_level_key(self):
        self.assertIn('amcl', self.data)

    def test_frames(self):
        params = self.data['amcl']['ros__parameters']
        self.assertEqual(params['global_frame_id'], 'map')
        self.assertEqual(params['odom_frame_id'], 'odom')
        self.assertEqual(params['base_frame_id'], 'base_footprint')

    def test_scan_topic(self):
        params = self.data['amcl']['ros__parameters']
        self.assertEqual(params['scan_topic'], 'scan')

    def test_laser_range(self):
        params = self.data['amcl']['ros__parameters']
        self.assertAlmostEqual(params['laser_max_range'], 1.5)
        self.assertAlmostEqual(params['laser_min_range'], 0.1)

    def test_differential_motion_model(self):
        params = self.data['amcl']['ros__parameters']
        self.assertEqual(params['robot_model_type'],
                         'nav2_amcl::DifferentialMotionModel')

    def test_initial_pose_matches_spawn(self):
        """Initial pose must match Gazebo spawn (0.0, 5.0, 0.0)."""
        params = self.data['amcl']['ros__parameters']
        initial_pose = params['initial_pose']
        self.assertAlmostEqual(initial_pose['x'], 0.0)
        self.assertAlmostEqual(initial_pose['y'], 5.0)
        self.assertAlmostEqual(initial_pose['yaw'], 0.0)
        self.assertTrue(params['set_initial_pose'])

    def test_use_sim_time(self):
        params = self.data['amcl']['ros__parameters']
        self.assertTrue(params['use_sim_time'])


class TestNav2Params(unittest.TestCase):
    """Validate config/nav2_params.yaml."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(_pkg_root(), 'config', 'nav2_params.yaml')
        with open(path, 'r') as f:
            cls.data = yaml.safe_load(f)

    # --- Top-level keys -----------------------------------------------
    def test_required_sections(self):
        for key in ('bt_navigator', 'planner_server', 'controller_server',
                     'behavior_server', 'global_costmap', 'local_costmap'):
            self.assertIn(key, self.data, f'Missing section: {key}')

    # --- Frame consistency --------------------------------------------
    def test_base_frame_consistency(self):
        """All components must use base_footprint."""
        checks = [
            self.data['bt_navigator']['ros__parameters']['robot_base_frame'],
            self.data['behavior_server']['ros__parameters']['robot_base_frame'],
            self.data['global_costmap']['global_costmap']
                ['ros__parameters']['robot_base_frame'],
            self.data['local_costmap']['local_costmap']
                ['ros__parameters']['robot_base_frame'],
        ]
        for val in checks:
            self.assertEqual(val, 'base_footprint')

    def test_global_frame_consistency(self):
        self.assertEqual(
            self.data['bt_navigator']['ros__parameters']['global_frame'],
            'map')
        self.assertEqual(
            self.data['global_costmap']['global_costmap']
                ['ros__parameters']['global_frame'], 'map')

    def test_local_costmap_odom_frame(self):
        params = self.data['local_costmap']['local_costmap']['ros__parameters']
        self.assertEqual(params['global_frame'], 'odom')

    # --- Planner plugin -----------------------------------------------
    def test_navfn_planner(self):
        params = self.data['planner_server']['ros__parameters']
        self.assertIn('GridBased', params)
        self.assertEqual(params['GridBased']['plugin'],
                         'nav2_navfn_planner/NavfnPlanner')

    # --- Controller plugin --------------------------------------------
    def test_dwb_controller(self):
        params = self.data['controller_server']['ros__parameters']
        self.assertIn('FollowPath', params)
        self.assertEqual(params['FollowPath']['plugin'],
                         'dwb_core::DWBLocalPlanner')

    # --- Behavior plugins ---------------------------------------------
    def test_behavior_plugins(self):
        params = self.data['behavior_server']['ros__parameters']
        self.assertIn('spin', params)
        self.assertIn('backup', params)
        self.assertIn('wait', params)
        self.assertEqual(params['spin']['plugin'], 'nav2_behaviors/Spin')
        self.assertEqual(params['backup']['plugin'], 'nav2_behaviors/BackUp')
        self.assertEqual(params['wait']['plugin'], 'nav2_behaviors/Wait')

    # --- Costmap layers -----------------------------------------------
    def test_global_costmap_layers(self):
        params = self.data['global_costmap']['global_costmap']['ros__parameters']
        self.assertIn('static_layer', params['plugins'])
        self.assertIn('obstacle_layer', params['plugins'])
        self.assertIn('inflation_layer', params['plugins'])

    def test_local_costmap_layers(self):
        params = self.data['local_costmap']['local_costmap']['ros__parameters']
        self.assertIn('obstacle_layer', params['plugins'])
        self.assertIn('inflation_layer', params['plugins'])
        # Local costmap must NOT have static_layer
        self.assertNotIn('static_layer', params['plugins'])

    # --- Scan topic consistency ---------------------------------------
    def test_scan_topic_in_costmaps(self):
        """Both costmaps must subscribe to /scan."""
        for section in ('global_costmap', 'local_costmap'):
            params = self.data[section][section]['ros__parameters']
            topic = params['obstacle_layer']['scan']['topic']
            self.assertEqual(topic, '/scan',
                             f'{section} obstacle_layer scan topic mismatch')

    # --- Footprint consistency ----------------------------------------
    def test_footprint_consistency(self):
        """Global and local costmaps must have the same footprint."""
        gp = self.data['global_costmap']['global_costmap'] \
            ['ros__parameters']['footprint']
        lp = self.data['local_costmap']['local_costmap'] \
            ['ros__parameters']['footprint']
        self.assertEqual(gp, lp)

    # --- use_sim_time everywhere --------------------------------------
    def test_use_sim_time(self):
        for section in ('bt_navigator', 'planner_server',
                         'controller_server', 'behavior_server'):
            params = self.data[section]['ros__parameters']
            self.assertTrue(params['use_sim_time'],
                            f'{section} must have use_sim_time: true')


class TestBehaviorTreeXML(unittest.TestCase):
    """Validate behavior_trees/navigate_to_pose.xml."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(_pkg_root(), 'behavior_trees',
                            'navigate_to_pose.xml')
        cls.tree = ET.parse(path)
        cls.root = cls.tree.getroot()

    def test_root_tag(self):
        self.assertEqual(self.root.tag, 'root')

    def test_main_tree_attribute(self):
        self.assertEqual(self.root.attrib['main_tree_to_execute'], 'MainTree')

    def test_behavior_tree_exists(self):
        bt = self.root.find('.//BehaviorTree[@ID="MainTree"]')
        self.assertIsNotNone(bt, 'BehaviorTree with ID="MainTree" not found')

    def test_compute_path_node(self):
        node = self.root.find('.//ComputePathToPose')
        self.assertIsNotNone(node)
        self.assertEqual(node.attrib.get('planner_id'), 'GridBased')

    def test_follow_path_node(self):
        node = self.root.find('.//FollowPath')
        self.assertIsNotNone(node)
        self.assertEqual(node.attrib.get('controller_id'), 'FollowPath')

    def test_recovery_actions(self):
        """All four recovery behaviors must be present."""
        for tag in ('ClearEntireCostmap', 'Spin', 'Wait', 'BackUp'):
            nodes = self.root.findall(f'.//{tag}')
            self.assertTrue(len(nodes) > 0, f'{tag} node not found in BT')


class TestPackageXML(unittest.TestCase):
    """Validate package.xml structure."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(_pkg_root(), 'package.xml')
        cls.tree = ET.parse(path)
        cls.root = cls.tree.getroot()

    def test_package_name(self):
        name = self.root.find('name')
        self.assertIsNotNone(name)
        self.assertEqual(name.text, 'testbed_navigation')

    def test_build_type(self):
        export = self.root.find('export')
        self.assertIsNotNone(export)
        bt = export.find('build_type')
        self.assertIsNotNone(bt)
        self.assertEqual(bt.text, 'ament_python')

    def test_critical_dependencies(self):
        """Key runtime dependencies must exist in depend or exec_depend."""
        deps = {d.text for d in self.root.findall('exec_depend')} | \
               {d.text for d in self.root.findall('depend')}
        required = {
            'nav2_map_server', 'nav2_amcl', 'nav2_planner',
            'nav2_controller', 'nav2_bt_navigator', 'nav2_behaviors',
            'nav2_lifecycle_manager', 'nav2_msgs',
        }
        missing = required - deps
        self.assertFalse(missing, f'Missing dependency in package.xml: {missing}')


if __name__ == '__main__':
    unittest.main()

import os
from glob import glob
from setuptools import setup, find_packages

package_name = 'testbed_navigation'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
        (os.path.join('share', package_name, 'behavior_trees'),
            glob('behavior_trees/*.xml')),
        (os.path.join('share', package_name, 'rviz'),
            glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kunal',
    maintainer_email='kunal.j@ericrobotics.com',
    description='Nav2 navigation package for Testbed-T1.0.0 robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigation_client = testbed_navigation.navigation_client:main',
            'navigation_manager = testbed_navigation.navigation_manager:main',
            'navigation_monitor = testbed_navigation.navigation_monitor:main',
            'navigation_test = testbed_navigation.navigation_test:main',
        ],
    },
)

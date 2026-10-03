# Testbed Navigation

This package provides manual navigation bringup launch files for the `Testbed-T1.0.0` robot.
It uses Nav2 plugins manually instead of the `nav2_bringup` convenience package.

## Components

- **Map Loader**: Loads the provided map using `nav2_map_server`.
- **Localization**: Localizes the robot in the map using `nav2_amcl`.
- **Navigation**: Brings up the planner (`nav2_navfn_planner`), controller (`nav2_regulated_pure_pursuit_controller`), behavior server, and BT navigator.

## Usage

1. Launch the testbed environment:
   ```bash
   ros2 launch testbed_bringup testbed_full_bringup.launch.py
   ```

2. Load the map:
   ```bash
   ros2 launch testbed_navigation map_loader.launch.py
   ```

3. Launch localization:
   ```bash
   ros2 launch testbed_navigation localization.launch.py
   ```
   *Note: Ensure you set the initial pose in RViz or it will use the `initial_pose` set in `amcl_params.yaml`.*

4. Launch navigation:
   ```bash
   ros2 launch testbed_navigation navigation.launch.py
   ```

You can now use the "Nav2 Goal" tool in RViz to issue navigation commands to the robot.

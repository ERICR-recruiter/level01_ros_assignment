# testbed_navigation
Manual Nav2 bringup for Testbed-T1.0.0 (no nav2_bringup).

## Run
1. `ros2 launch testbed_bringup testbed_full_bringup.launch.py`
2. `ros2 launch testbed_navigation map_loader.launch.py`      (map only, to verify the map in RViz)
3. `ros2 launch testbed_navigation localization.launch.py`    (map_server + AMCL; stop #2 first)
4. `ros2 launch testbed_navigation navigation.launch.py`
Set the 2D Pose Estimate in RViz, then send a Nav2 Goal.

## Design
- map_loader: map_server + lifecycle_manager
- localization: map_server + amcl + lifecycle_manager
- navigation: controller_server (Regulated Pure Pursuit), planner_server (NavFn), behavior_server, bt_navigator + lifecycle_manager

## Challenges
- Bug in the starter code: see bugs_found.txt in the repo root.

## Contact
- GitHub: RithwikaPG
- Email: rithvikapg@gmail.com

## Demo video
https://drive.google.com/drive/folders/1j8uCvCQ8kII3YWM2lFSHlv87d4A5iiQ2

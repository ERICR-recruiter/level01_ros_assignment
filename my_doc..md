1.Forked the repo and cloned the fork on my local machine.
2.Checked the dependencies and versions for making a compatible environment
3.Gazebo version mismatched, installed the required version 11.10.2
4.Build the workspace.
5.Encountered first bug: 
--- stderr: testbed_description
CMake Error at CMakeLists.txt:24:
  Parse error.  Expected "(", got newline with text "

  ".
6.Added () after ament_package
7.Build successful
8.Ran the bringup launch file. Rviz and Gazebo successfully opened.
9.Create the new package testbed_navigation
10.Made the config and launch directories as they are clearly required as per the provided readme.md
11.Read the map_server plugin doc
12.While reading the testbed_world.yaml file found that the location of map is wrong so I added the absolute path of the map. Now I can try loading the map using map_server plugin directly through terminal as per commands given in the documentation first before making the launch file.
13.map_server plugin is not pre installed, installing it.
14.Ran into an error, the plugin was looking for the map from where the yaml file was, so absolute path didnt work so added relative path. Map loaded in rviz2 successfully just figured out we always need to configure it using "ros2 lifecycle set /map_server configure" command to transition /map_server topic to /map topic so need to add this action in the launch file.
15.Debugged the launch file so it finally loads the map properly and checked it on rviz2.
16.Reading the AMCL plugin docs to figure out the parameters required to be in the yaml file.
17.Running the Amcl plugin to test it before making the launch file.
18.Debugged the run and verified it is running properly, now making the launch file.
19.Made the launch file so that it build everything from ground up till the amcl implementation.
20.Successfully tested the launch file.
21.Looking for what plugins should be used for navigation.
22.Decided the plugins and writen the params required for them.
23.Tested navigation before navigation before creating the launch file.
24.Fixed the error in parameters. But the planner is reporting error it couldnt plan.
25.The cause of the error narrowed down to being the range of LiDAR in the urdf.
26.Tested different ranges, and finally settld down to 10. Which makes navigation work successfully.
27.Creating the launch file.
28.Noticed that the bringup launch is not able to open rviz2 so I should fix that.
29.Changed the localization.launch.py to preset the initial pose to makes thing convinient.
30.Ran the implementation successfully. Now will add this doc as the readme.md in testbed_navigation directory.
31.Attached a video in the implementation video directory.

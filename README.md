# Level 1: ROS2 Navigation Assignment - Karv Amin

### 1. Solving the Bugs
1. To first identify the bugs in the files. I made an empty directory and added the src directory. The forked github repo was cloned inside the src.
2. Afterwards I colcon build it, while doing this I encountered a missing parenthesis error in cmakelists.txt of testbed_description package in the last line.
3. Then while trying to run the robot bringup I found one ros1 control plugin being used in testbed.gazebo in urdf and one more indentation error in the same file in the imu_link_1 's orientation reference.
4. The name in the yaml file of the map mismatched with the name of the pgm image, I couldn't find any more bugs after this.


### 2. Setting up the map loader launch file
1. As I couldn't use the nav2_bringup, I made a launch file that uses the nav2 map_server node to launch the testbed_world map. I followed the instructions and named it map_loader.launch.py.
2. In rviz , I would have to change it settings to transient_local and type map into fixed frame to visualize it because without amcl the odom to map tf connection isn't developed yet. Then map would be visible in rviz.

![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-21-27.png)

### 3. Launching Amcl
1. For this I made an amcl_params.yaml to define the parameters of the amcl. I increased the range of lidar in testbed.gazebo as its inital range was too small for any localization operation.
2. Then after reading  the nav2 official github that defined the amcl launch file, I use that as reference to make a localization.launch.py that would launch the amcl nodes and initialize it.
3. Initially after launching amcl, In rviz I would try to give 2d pose manually after setting fixed frame as map. As the transform between odom and map gets established, rviz crashes and then after reopening it I can see the robot at the pose I had given before.
4. But to keep things consistent I set inital_pose to true in yaml to immediately set up the tf connection between map and odom . This would stop rviz from crashing suddenly and map would be visible in rviz and without the need of manually typing map in fixed frame.
5. After launching localization, the robot would be at the pose mentioned in the yaml but I correct it again manually if actual pose is different. Then I moved the robot around with teleop and amcl seemed to be working properly.

![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-24-08.png)

### 4. Navigation
1. For navigation I made a nav2_prarams.yaml file describing the robot's parameters properly. I only kept those servers in the yaml that i felt were absolutely necessary to make the robot navigate properly.
2. Then I made a navigation.launch.py launch file launching those exact same nodes and a lifecycle manager node to manage them. On launching the nav2 seemed to work properly.
3. Then I gave the 2d goal pose, the robot seemed to operate normally. In the navigation panel both localization and navigation seemed to be working properly.

![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-26-17.png)

![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-26-34.png)

### Video
[![Watch the navigation demo video](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-26-34.png)](screenshots%20and%20videos/Screencast%20from%2009-25-2026%2010_18_53%20AM.mp4)

## Contact Info 
 - Name: Karv Amin
 - Contact number: 9586866647
 - Email Address: karvamin@gmail.com

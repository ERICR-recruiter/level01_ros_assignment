# Level 1: ROS2 Navigation Assignment - Karv Amin

### 1. Solving the Bugs
1. To first identify the bugs in the files. I made an empty directory and added the src directory. The forked github repo was cloned inside the src.
2. Afterwards I colcon build it, while doing this I encountered a missing parenthesis error in cmakelists.txt of testbed_description package in the last line.
3. Then while trying to run the robot bringup I found one ros1 control plugin being used in testbed.gazebo in urdf and one more indentation error in the same file in the imu_link_1 's orientation reference.
4. The name in the yaml file of the map mismatched with the name of the pgm image, I couldn't find any more bugs after this.


### 2. Setting up the map loader script
1. As I couldnt use the nav2_bringup, I made a launch file that uses the nav2 map_server node to launch the testbed_world map. I followed the instructions and named it map_loader.launch.py.
![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-21-27.png)

### 3. Launching Amcl
1. For this I made a amcl_params.yaml to define the parameters of the amcl.
2. Then using the nav2 official github that defined the amcl as reference, I made a localization.launch.py that would launch the amcl.
3. Initially I after launching amcl i was unable to develop the tf connection between map and robot's odom. I had initial pose as false in yaml to give 2d pose manually but the rviz would crash right afterwards. So, I gave an initial pose in the yaml to start that tf connection and amcl seemed to work properly after this change.
4. Then I increased the range of lidar in testbed.gazebo as its inital range was too small for any localization operation. After launching localization i would then manually give correct the robot pose using 2d pose estimate.  
![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-24-08.png)

### 4. Navigation
1. For navigation I made a nav2_prarams.yaml file describing the robot's parameters properly. I only kept those servers in the yaml that i felt were absolutely necessary to make the robot navigate properly.
2. Then I made a navigation.launch.py launch file launching those exact same nodes and a lifecycle manager node to manage them. On launching the nav2 seemed to work properly.
![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-26-17.png)

![My Screenshot](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-26-34.png)

### Video
[![Watch the navigation demo video](screenshots%20and%20video/Screenshot%20from%202026-09-25%2011-26-34.png)](screenshots%20and%20videos/Screencast%20from%2009-25-2026%2010_18_53%20AM.mp4)

## Contact Info 
 - Name: Karv Amin
 - Contact number: 9586866647
 - Email Address: karvamin@gmail.com

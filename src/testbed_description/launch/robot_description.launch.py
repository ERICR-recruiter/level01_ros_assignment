#!/usr/bin/env python3

from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue #Changes--> importing ParamterValue to solve the entire XML document to passed as one string paramter #


def generate_launch_description():

    ## launching urdf data here 

    #Changes --> Added ParameterValue , removed PathJoinSubstution 
    robot_description_content = ParameterValue(
        Command([ 
        FindExecutable(name="xacro"),  ## locates the xacro command on system
        " ",
        PathJoinSubstitution([
            FindPackageShare("testbed_description"),
            "urdf",
            "testbed.xacro",
            ]), ## identifying the location of testbed.xacro
    ]),
     value_type=str
     ) ## processing the xacro into a Urdf description

    ## starting joint state publisher actions 
    robot_description = {"robot_description": robot_description_content}  ## pass the description to robot_state_publisher
    
    
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description, {'use_sim_time': True}]), #-> Changes --> added use_sim_time true#
    ])



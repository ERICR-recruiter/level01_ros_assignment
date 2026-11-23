import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, LaunchConfiguration  #-Change# imported LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument   #-Change# imported DeclareLaunchArgument 
from launch_ros.parameter_descriptions import ParameterValue 

# this is the function launch the system will look for
def generate_launch_description():


      ####### DATA INPUT ##########
    urdf_file = 'testbed.xacro'
    package_description = "testbed_description"

    print("Fetching URDF ==>")
    robot_desc_path = os.path.join(
        get_package_share_directory(package_description), "urdf", urdf_file)

    #-Changes -> Adding Paramter Value to solve 
    """[ERROR] [launch]: Caught exception in launch (see debug for traceback): Unable to parse the value of parameter robot_description as yaml.
      If the parameter is meant to be a string, try wrapping it in launch_ros.parameter_descriptions.ParameterValue(value, value_type=str) """
    
    robot_description_content = ParameterValue(
        Command(['xacro ', robot_desc_path]),
        value_type=str,
    )


    #ROBOT STATE PUBLISHER
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 
                     'robot_description': robot_description_content, 
                     }],
        output="screen"
    )

    #-Changes done#

    #JOINT STATE PUBLISHER
    joint_state_controller_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
            # parameters=[
            #     {'use_sim_time': LaunchConfiguration('use_sim_time')}
            # ] #since galactic use_sim_time gets passed somewhere and rejects this when defined from launch file
    ) ## node publishes joint position of robot wheel with /joint_states topic
    
    #RVIZ CONFIGURATION
    rviz_config_dir = os.path.join(
        get_package_share_directory(package_description),
        'rviz',
        'testbed_barebones.rviz')
    
    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            output="screen", #-Change --> added this line#
            arguments=['-d', rviz_config_dir]

    ) ## starts Rviz and loads the configuration

    # create and return launch description object
    return LaunchDescription([        
            
            # robot_state_publisher_node,
            # joint_state_controller_node,
            rviz_node,
    ])

#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():

    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    rviz_config = LaunchConfiguration("rviz_config")

    # Path to files

    # Path to the robot package
    description_pkg = "my_robot_pkg"
    description_share = get_package_share_directory(description_pkg)
    
    # Path to the robot URDF file
    urdf_file = os.path.join(description_share, "urdf", "diffbot_description.urdf")

    # Path to the default RViz config file
    default_rviz_config_path = os.path.join(
        description_share,
        "rviz",
        "diffbot.rviz",
    )

    # Lee el contenido del URDF de forma robusta
    try:
        with open(urdf_file, 'r') as inf:
            robot_description_content = inf.read()
    except Exception as e:
        robot_description_content = ''
        print(f"[ERROR] No se pudo leer el URDF: {e}")


    # Declaration of the rviz configuration file, can be overridden by user
    declare_rviz_config = DeclareLaunchArgument(
        name="rviz_config",
        default_value=default_rviz_config_path,
        description="Path to the RViz config file",
    )

    # Time synchronization argument for simulation
    declare_use_sim_time = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="false",
        description="Use simulation (Gazebo) clock if true",
    )

    # Nodes to launch

     # Nodo joint_state_publisher

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"robot_description": robot_description_content},
        ],
    )


    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time, "gui": True}],
    )



    # Solo pasa el argumento -d si el archivo existe
    rviz_arguments = []
    if os.path.exists(default_rviz_config_path):
        rviz_arguments = ["-d", default_rviz_config_path]

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=rviz_arguments,
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # Path to controller config
    controller_config = os.path.join(description_share, "control", "controller_manager.yaml")

    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": robot_description_content},
            controller_config,
            {"use_sim_time": use_sim_time}
        ],
        output="screen"
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen"
    )

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_base_controller"],
        output="screen"
    )
    # Orden correcto: primero publishers, luego RViz
    return LaunchDescription([
        declare_use_sim_time,
        declare_rviz_config,
        robot_state_publisher_node,
        joint_state_publisher_node,
        rviz_node,
        controller_manager_node,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
    ])


    
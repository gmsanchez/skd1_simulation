"""Launch Gazebo server and client via include and launch the gazebo.launch.py file."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, AppendEnvironmentVariable, RegisterEventHandler, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit

from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
from pathlib import Path


def generate_launch_description():
    
    empty_world = PathJoinSubstitution([FindPackageShare("skd1_gz"), "worlds", "empty_world.world"],)

    ARGUMENTS = [
        DeclareLaunchArgument('use_sim_time', default_value='true',
                          description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument('world_path', default_value=empty_world,
                          description='The world path, by default is empty.world'),
        DeclareLaunchArgument('x', default_value='0',
                          description='x-axis initial position'),
        DeclareLaunchArgument('y', default_value='0',
                          description='y-axis initial position'),
        DeclareLaunchArgument('z', default_value='0.17',
                          description='z-axis initial position'),
        DeclareLaunchArgument('yaw', default_value='0',
                          description='YAW initial orientation'),
    ]
    
    world_path = LaunchConfiguration('world_path')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    yaw = LaunchConfiguration('yaw')
    
    gz_resource_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        PathJoinSubstitution([FindPackageShare("skd1_gz"), "models"]),
    )
    
    # Launch Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py']),
        ),
        launch_arguments={'gz_args': ['-r -v 4 ', world_path]}.items()
        # launch_arguments={'gz_args': ['-r -v 4 ', world_path], 'on_exit_shutdown': 'true'}.items()
    )
    
    # Launch robot_state_publisher
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('skd1_description'), 'launch', 'skd1_description_launch.py']),
        ),
        launch_arguments= {'use_sim_time': use_sim_time}.items(),
    )
    
    spawn_skd1_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-entity", "skd1",
            "-topic", "robot_description",
            "-x", x,
            "-y", y,
            "-z", z,
            "-Y", yaw,
        ],
        output="screen",
        parameters=[{ 'use_sim_time': use_sim_time}],
    )

    spawn_skd1_velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "skd1_base_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
        parameters=[{ 'use_sim_time': use_sim_time}],
    )
    
    spawn_skd1_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
        parameters=[{ 'use_sim_time': use_sim_time}],
    )
    
    # Delay start of `joint_state_broadcaster` after spawn_skd1_entity
    # delay_joint_state_broadcaster_after_skd1_entity = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=spawn_skd1_joint_state_broadcaster,
    #         on_exit=[spawn_skd1_entity],
    #     )
    # )
    
    # Delay start of velocity_controller after `joint_state_broadcaster`
    delay_velocity_controller_after_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_skd1_joint_state_broadcaster,
            on_exit=[spawn_skd1_velocity_controller],
        )
    )
    
    # load_joint_state_broadcaster = ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
    #          'joint_state_broadcaster'],
    #     output='screen'
    # )

    # load_diff_drive_controller = ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
    #          'skd1_base_controller'],
    #     output='screen'
    # )
    
    # delay_joint_state_broadcaster_spawner_after_entity_spawner =  RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=spawn_skd1_entity,
    #         on_exit=[load_joint_state_broadcaster],
    #     )
    # )
    # delay_diff_drive_controller_spwanwer_after_joint_state_broadcaster_spawner = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=load_joint_state_broadcaster,
    #         on_exit=[load_diff_drive_controller],
    #     )
    # )
      
    # Bridge
    # Topics: The first @ symbol delimits the topic name from the message types.
    # [parameter_bridge-4] Following the first @ symbol is the ROS message type.
    # [parameter_bridge-4] The ROS message type is followed by an @, [, or ] symbol where
    # [parameter_bridge-4]     @  == a bidirectional bridge, 
    # [parameter_bridge-4]     [  == a bridge from Gazebo to ROS,
    # [parameter_bridge-4]     ]  == a bridge from ROS to Gazebo.
    
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                   '/ardusimple/fix@sensor_msgs/msg/NavSatFix@gz.msgs.NavSat',
                   '/mti_630_8A1G6/imu/data@sensor_msgs/msg/Imu@gz.msgs.IMU',
                   '/mti_630_8A1G6/imu/mag@sensor_msgs/msg/MagneticField@gz.msgs.Magnetometer',
                   '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
                   '/scan/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked'
                ],
        output='screen'
    )   
 
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gz_resource_path)
    ld.add_action(gz_sim)
    ld.add_action(gz_bridge)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_skd1_entity)
    ld.add_action(spawn_skd1_joint_state_broadcaster)
    ld.add_action(delay_velocity_controller_after_joint_state_broadcaster)
    # ld.add_action(delay_joint_state_broadcaster_spawner_after_entity_spawner)
    # ld.add_action(delay_diff_drive_controller_spwanwer_after_joint_state_broadcaster_spawner)

    return ld

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

import math

def generate_launch_description():
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    
    ARGUMENTS = [
      DeclareLaunchArgument('slam_param_files', default_value=PathJoinSubstitution([FindPackageShare('skd1_navigation'), 'config', 'mapper_params_online_async.yaml']),
            description='Full path to param yaml file to load for SLAM Online Async'),
      DeclareLaunchArgument('nav2_params_file', default_value=PathJoinSubstitution([FindPackageShare('skd1_navigation'), 'config', 'nav2_params.yaml']),
            description='Full path to param yaml file to load for Nav2'),
    ]
    
    slam_params_file = LaunchConfiguration('slam_param_files')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    
    spawn_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            # '--ros-args', '--log-level', 'debug',
        ],
    )
    
    skd1_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("skd1_description"),
                "launch",
                "skd1_description_launch.py"
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )
    
    teleop_joy_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("skd1_teleop"),
                "launch",
                "skd1_teleop_twist_joy_launch.py"],
            )
        ),
        launch_arguments= {'use_sim_time': use_sim_time}.items(),
    )

    teleop_twist_mux_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
            [FindPackageShare("skd1_teleop"),
                "launch",
                "skd1_twist_mux_launch.py"],
            )
        ),
        launch_arguments= {'use_sim_time': use_sim_time}.items(),
    )
    
    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("skd1_localization"),
                "launch",
                "ekf_launch.py"],
            )
        ),
        launch_arguments= {'use_sim_time': use_sim_time}.items(),
    )

    ekf_global_map_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("skd1_localization"),
                "launch",
                "ekf_global_map_launch.py"],
            )
        ),
        launch_arguments= {'use_sim_time': use_sim_time}.items(),
    )
    
    online_async_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam_toolbox"),
                "launch",
                "online_async_launch.py"],
            )
        ),
        launch_arguments= {'use_sim_time': use_sim_time,
                        'slam_params_file': slam_params_file}.items(),
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('skd1_navigation'),
                'launch',
                'navigation_launch.py']),
        ),
        launch_arguments = {'use_sim_time': use_sim_time,
                            'params_file': nav2_params_file}.items()
    )
   

    ld = LaunchDescription(ARGUMENTS)
    # ld.add_action(spawn_joint_state_broadcaster)
    # ld.add_action(skd1_description)
    ld.add_action(teleop_twist_mux_launch)
    ld.add_action(teleop_joy_launch)
    ld.add_action(ekf_launch)
    ld.add_action(ekf_global_map_launch)
    ld.add_action(online_async_launch)
    ld.add_action(nav2_launch)

    return ld
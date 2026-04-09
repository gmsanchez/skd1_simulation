from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

import math

def generate_launch_description():
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    
    ARGUMENTS = []
    
    world_file = PathJoinSubstitution(
        [FindPackageShare("skd1_gz"),
        "worlds",
        "small_warehouse.world"],
    )

    gz_launch = PathJoinSubstitution(
        [FindPackageShare("skd1_gz"),
        "launch",
        "skd1_gz_launch.py"],
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_launch]),
        launch_arguments = {
            'world_path': world_file,
            'x': '0.0',
            'y': '-2.0',
            'z': '0.13',
            'yaw': str(math.pi/2.0),
        }.items(),
    )
    
    gz_nav2_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(
         PathJoinSubstitution(
            [FindPackageShare("skd1_gz"),
             "launch",
             "skd1_gz_nav2_launch.py"],
         )
      ),
      launch_arguments= {'use_sim_time': use_sim_time}.items(),
   )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gz_sim)
    ld.add_action(gz_nav2_launch)

    return ld
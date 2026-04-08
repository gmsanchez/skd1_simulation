from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

import math

def generate_launch_description():
    
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
            'yaw': str(math.pi/2.0),
        }.items(),
    )

    ld = LaunchDescription([])
    ld.add_action(gz_sim)

    return ld
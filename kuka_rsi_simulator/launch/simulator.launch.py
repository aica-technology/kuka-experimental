from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    host_ip = DeclareLaunchArgument(
        "host_ip", description="Host IP", default_value="127.0.0.1"
    )
    port = DeclareLaunchArgument(
        "port", description="Port", default_value="49152"
    )

    sim_node = Node(
        package="kuka_rsi_simulator",
        executable="simulator",
        name="sim",
        arguments=[LaunchConfiguration("host_ip"), LaunchConfiguration("port")],
        output="log",
    )

    return LaunchDescription([host_ip, port] + [sim_node])

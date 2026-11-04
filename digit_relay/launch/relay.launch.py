from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='digit_relay',
            executable='relay1',
            name='relay1',
        ),
        Node(
            package='digit_relay',
            executable='relay2',
            name='relay2',
        ),
        Node(
            package='digit_relay',
            executable='relay3',
            name='relay3',
        ),
        Node(
            package='digit_relay',
            executable='relay4',
            name='relay4',
        ),
])
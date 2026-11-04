import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

def main(args = None):
    rclpy.init(args=args)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
import rclpy
from dataclasses import dataclass
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen
from turtlesim.action import RotateAbsolute
from relay_interfaces.msg import RelayToken

@dataclass
class Point2d:
    x: float
    y: float

digit_paths_unit = [
    # 0
    [],
    # 1
    [],
    # 2
    [],
    # 3
    [],
    # 4
    [],
    # 5
    [],
    # 6
    [],
    # 7
    [],
    # 8
    [],
    # 9
    []
]

AREA_WIDTH = 5.5
AREA_HEIGHT = 5.5
AREA_OFFSET_X = 0
AREA_OFFSET_Y = 0




class Relay1(Node):
    def __init__(self):
        super().__init__('relay1')

        self.current_number = 1
        
        self.pen_rgb = [100, 255, 210]

        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.turtlesim_pose_callback, 10);
        self.pose = None
        self.set_pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        while not self.set_pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /turtle1/set_pen service...')
        self.set_pen_req = SetPen.Request()
        self.set_pen_req.r, self.set_pen_req.g, self.set_pen_req.b = self.pen_rgb
    def turtlesim_pose_callback(self, msg : Pose):
        self.pose = msg
    def set_pen(self, off : bool):
        self.set_pen_req.off = off
        future = self.set_pen_client.call_async(self.set_pen_req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()
    


def main(args = None):
    rclpy.init(args=args)
    relay_node = Relay1()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
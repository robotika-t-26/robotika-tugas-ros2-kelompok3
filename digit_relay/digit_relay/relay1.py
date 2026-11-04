import rclpy
import time
from rclpy.wait_for_message import wait_for_message
import math
from dataclasses import dataclass
from rclpy.node import Node
from rclpy.action import ActionClient
from std_srvs.srv import Empty
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, TeleportAbsolute
from relay_interfaces.msg import RelayToken

class CycleFinish(Exception):
    pass

@dataclass
class Point2d:
    x: float
    y: float

digit_paths_unit : list[Point2d] = [
    # 0
    [],
    # 1
    [Point2d(0.5, 0.2), Point2d(0.5, 0.8)],
    # 2
    [],
    # 3
    [],
    # 4
    [],
    # 5
    [
        Point2d(0.8, 0.2), Point2d(0.2, 0.2), Point2d(0.2, 0.5), Point2d(0.6, 0.5), 
        Point2d(0.8, 0.65), Point2d(0.6, 0.8), Point2d(0.2, 0.8)
        ],
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

digit_paths_scaled : list[list[Point2d]] = []

for path in digit_paths_unit:
    scaled_path = []
    for point in path:
        scaled_path.append(Point2d(point.x * AREA_WIDTH + AREA_OFFSET_X, point.y * AREA_HEIGHT + AREA_OFFSET_Y))
    digit_paths_scaled.append(scaled_path)



class Relay1(Node):
    def __init__(self):
        super().__init__('relay1')
        self.busy = False
        self.node_id = 1
        self.total_members = 4

        self.active_member = 1
        self.current_number = 1
        self.draw_line_duration = 0.5
        
        self.pen_rgb = [100, 255, 210]
        
        self.turn_pub = self.create_publisher(RelayToken, '/turn_status', 10)
        init_turn_msg = RelayToken()
        init_turn_msg.active_member = self.active_member
        init_turn_msg.current_number = self.current_number
        self.turn_pub.publish(init_turn_msg)
        self.turn_sub = self.create_subscription(
            RelayToken, 
            '/turn_status', 
            self.turn_callback, 
            10
        )

        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.turtlesim_pose_callback, 10);
        self.pose : Pose | None = None
        self.clear_client = self.create_client(Empty, '/clear')
        while not self.clear_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /clear service...')
        self.set_pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        while not self.set_pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /turtle1/set_pen service...')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        while not self.teleport_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /turtle1/teleport_absolute service...')

        self.clear_req = Empty.Request()
        self.set_pen_req = SetPen.Request()
        self.set_pen_req.r, self.set_pen_req.g, self.set_pen_req.b = self.pen_rgb
        self.timer = self.create_timer(0.1, self.run_turn)

    def request_clear(self):
        self.future = self.clear_client.call_async(self.clear_req)
    def teleport_to(self, x: float, y: float, theta: float = 0.0):
            if not self.teleport_client.service_is_ready():
                return
            req = TeleportAbsolute.Request()
            req.x = x
            req.y = y
            req.theta = theta
            self.teleport_client.call_async(req)
            time.sleep(0.1)

    def turn_callback(self, msg):
        if msg.current_number == self.total_members + 1:
            self.request_clear()
        elif msg.current_number > self.total_members * 2:
            raise CycleFinish
        self.active_member = msg.active_member
        self.current_number = msg.current_number

    def turtlesim_pose_callback(self, msg : Pose):
        self.pose = msg

    def set_pen(self, off : bool):
        self.set_pen_req.off = off
        self.future = self.set_pen_client.call_async(self.set_pen_req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()
    
    def drive_straight_to(self, x: float, y: float):
        if self.pose == None:
            self.get_logger().info(f'Pose not obtained')
            return
        twist_msg = Twist()
        angle = math.atan2(self.pose.x - x, self.pose.y - y)
        self.teleport_to(self.pose.x, self.pose.y, angle)
        distance = math.hypot(self.pose.x - x, self.pose.y - y)
        twist_msg.linear.x = distance / self.draw_line_duration

        end_time = time.time() + self.draw_line_duration
        while time.time() < end_time:
            self.cmd_vel_pub.publish(twist_msg)
            time.sleep(0.05)
        twist_msg.linear.x = 0.0
        self.cmd_pub.publish(twist_msg)
        time.sleep(0.05)

    def draw_digit(self, digit):
        if digit > 9 or digit < 0:
            return
        self.set_pen(off=True)
        self.drive_straight_to(AREA_WIDTH/2 + AREA_OFFSET_X, AREA_HEIGHT/2 + AREA_OFFSET_Y)
        self.set_pen(off=False)
        used_list = digit_paths_scaled[digit]
        for point in used_list:
            self.drive_straight_to(point.x, point.y)



    def run_turn(self):
        if self.active_member == self.node_id and not self.busy:
            self.busy = True
            self.get_logger().info(f'Relay1 mulai menggambar angka {self.current_number}...')
            
            self.draw_digit(self.current_number)

            next_msg = RelayToken()
            next_msg.active_member = 2
            next_msg.current_number = self.current_number + 1
            self.turn_pub.publish(next_msg)

            self.get_logger().info(f'Relay1 selesai. Oper giliran ke Anggota 2 (angka {next_msg.current_number}).')

            self.busy = False
    


def main(args = None):
    rclpy.init(args=args)
    relay_node = Relay1()
    try:
        rclpy.spin(relay_node)
    except KeyboardInterrupt:
        pass
    except CycleFinish:
        relay_node.get_logger().info(f'Siklus telah selesai')
    except Exception as e:
        relay_node.get_logger().error(f'Node stopped with exception: {e}')
    finally:
        relay_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
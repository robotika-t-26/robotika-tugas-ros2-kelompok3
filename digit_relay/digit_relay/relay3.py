import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from relay_interfaces.msg import RelayToken
from turtlesim.srv import SetPen, TeleportAbsolute
import time

class relay3(Node):
    def __init__(self):
        super().__init__('relay3')
        self.node_id = 3
        self.total_members = 4
        
        self.active_member = 1
        self.current_number = 0

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.turn_pub = self.create_publisher(RelayToken, '/turn_status', 10)
        self.turn_sub = self.create_subscription(
            RelayToken, 
            '/turn_status', 
            self.turn_callback, 
            10
        )

        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')

        self.busy = False
        self.timer = self.create_timer(0.5, self.run_turn)

    def turn_callback(self, msg: RelayToken):
        self.active_member = msg.active_member
        self.current_number = msg.current_number

    def set_pen(self, off=0, r=0, g=255, b=0, width=4):
        if not self.pen_client.service_is_ready():
            return

        req = SetPen.Request()
        req.r = int(r)
        req.g = int(g)
        req.b = int(b)
        req.width = int(width)
        req.off = int(off)

        self.pen_client.call_async(req)

    def teleport_to(self, x: float, y: float, theta: float = 0.0):
        if not self.teleport_client.service_is_ready():
            return

        req = TeleportAbsolute.Request()
        req.x = float(x)
        req.y = float(y)
        req.theta = float(theta)

        self.teleport_client.call_async(req)
        time.sleep(0.1)

    def drive_straight(self, speed, duration):
        msg = Twist()
        msg.linear.x = float(speed)
        msg.angular.z = 0.0
        end_time = time.time() + duration
        while time.time() < end_time:
            self.cmd_pub.publish(msg)
            time.sleep(0.05)
        msg.linear.x = 0.0
        self.cmd_pub.publish(msg)
        time.sleep(0.05)

    def draw_digit(self, num):
        self.set_pen(off=1)
        time.sleep(0.1)

        if num == 3:
            self.teleport_to(x=1.0, y=4.5, theta=0.0)
            self.set_pen(off=0, r=0, g=255, b=0, width=4)
            self.drive_straight(speed=1.5, duration=0.8)

            self.teleport_to(x=2.2, y=4.5, theta=-1.5708)
            self.set_pen(off=0, r=0, g=255, b=0, width=4)
            self.drive_straight(speed=1.5, duration=0.8)

            self.teleport_to(x=2.2, y=3.3, theta=3.14159)
            self.set_pen(off=0, r=0, g=255, b=0, width=4)
            self.drive_straight(speed=1.5, duration=0.8)

            self.teleport_to(x=2.2, y=3.3, theta=-1.5708)
            self.set_pen(off=0, r=0, g=255, b=0, width=4)
            self.drive_straight(speed=1.5, duration=0.8)

            self.teleport_to(x=2.2, y=2.1, theta=3.14159)
            self.set_pen(off=0, r=0, g=255, b=0, width=4)
            self.drive_straight(speed=1.5, duration=0.8)

        elif num == 7:
            self.teleport_to(x=1.0, y=4.5, theta=0.0)
            self.set_pen(off=0, r=0, g=255, b=0, width=4)
            self.drive_straight(speed=1.5, duration=0.8)

            self.teleport_to(x=2.2, y=4.5, theta=-1.5708)
            self.set_pen(off=0, r=0, g=255, b=0, width=4)
            self.drive_straight(speed=1.5, duration=1.6)

        self.set_pen(off=1)
        time.sleep(0.1)

    def run_turn(self):
        if self.active_member == self.node_id and not self.busy:
            self.busy = True
            self.active_member = 0
            
            self.draw_digit(self.current_number)

            next_msg = RelayToken()
            next_msg.active_member = 4
            next_msg.current_number = self.current_number + 1
            self.turn_pub.publish(next_msg)

            self.get_logger().info(
                f'Next {next_msg.current_number})'
            )
            self.busy = False

def main(args=None):
    rclpy.init(args=args)
    node = relay3()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()

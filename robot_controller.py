#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class RobotControllerNode(Node):
    """
    Контроллер робота.
    Управляет движением на основе статуса от /robot_status.
    Публикует команды скорости в /cmd_vel с частотой 10 Hz.
    """
    
    def __init__(self):
        super().__init__('robot_controller_node')
        
        # Текущий статус робота
        self.current_status = "UNKNOWN"
        
        # Предыдущий статус для отслеживания изменений
        self.previous_status = ""
        
        # Publisher для команд скорости (10 Hz)
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        # Subscriber для статуса робота
        self.status_subscriber = self.create_subscription(
            String,
            '/robot_status',
            self.status_callback,
            10
        )
        
        # Таймер для публикации команд скорости (10 Hz = 0.1 сек)
        self.timer = self.create_timer(0.1, self.publish_cmd_vel)
        
        self.get_logger().info('Robot Controller Node started')
        self.get_logger().info('Waiting for robot status...')
    
    def status_callback(self, msg):
        """
        Обновляет текущий статус робота при получении нового сообщения.
        """
        self.current_status = msg.data
        
        # Логируем изменение статуса
        if self.current_status != self.previous_status:
            self.get_logger().info(f'Status received: {self.current_status}')
            self.previous_status = self.current_status
    
    def get_motion_command(self):
        """
        Определяет команду движения на основе текущего статуса.
        Возвращает объект Twist с соответствующими скоростями.
        """
        twist = Twist()
        
        # Определяем режим движения по статусу
        if self.current_status == "ALL OK":
            twist.linear.x = 0.3   # движение вперед
            twist.angular.z = 0.0   # без поворота
            
        elif self.current_status == "WARNING: Low battery":
            twist.linear.x = 0.1    # медленное движение
            twist.angular.z = 0.0    # без поворота
            
        elif self.current_status == "WARNING: Obstacle close":
            twist.linear.x = 0.0     # остановка
            twist.angular.z = 0.5     # поворот на месте (влево)
            
        elif self.current_status == "CRITICAL":
            twist.linear.x = 0.0      # полная остановка
            twist.angular.z = 0.0      # без поворота
            
        else:  # UNKNOWN или любой другой статус
            twist.linear.x = 0.0       # безопасная остановка
            twist.angular.z = 0.0
        
        return twist
    
    def publish_cmd_vel(self):
        """
        Публикует команду скорости в /cmd_vel.
        Вызывается каждые 0.1 секунды (10 Hz).
        """
        # Получаем команду движения для текущего статуса
        twist = self.get_motion_command()
        
        # Публикуем команду
        self.cmd_vel_publisher.publish(twist)
        
        # Логируем изменение режима работы (только при смене статуса)
        if hasattr(self, 'last_logged_status') and self.last_logged_status != self.current_status:
            mode_description = self.get_mode_description(self.current_status)
            self.get_logger().info(f'Mode changed: {mode_description}')
            self.last_logged_status = self.current_status
        elif not hasattr(self, 'last_logged_status'):
            self.last_logged_status = self.current_status
            mode_description = self.get_mode_description(self.current_status)
            self.get_logger().info(f'Initial mode: {mode_description}')
    
    def get_mode_description(self, status):
        """
        Возвращает человеко-читаемое описание режима работы.
        """
        descriptions = {
            "ALL OK": "Normal operation (0.3 m/s)",
            "WARNING: Low battery": "Economy mode (0.1 m/s)",
            "WARNING: Obstacle close": "Obstacle avoidance (turning)",
            "CRITICAL": "EMERGENCY STOP",
            "UNKNOWN": "Safe mode (stopped)"
        }
        return descriptions.get(status, "Unknown mode")


def main(args=None):
    rclpy.init(args=args)
    node = RobotControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

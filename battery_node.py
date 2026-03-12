#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class BatteryNode(Node):
    """
    Симулятор батареи робота.
    Равномерно разряжается на 1% каждую секунду.
    """
    
    def __init__(self):
        super().__init__('battery_node')
        
        # Начальный заряд
        self.battery_level = 100.0
        self.last_logged_percent = 100  # для отслеживания снижения на 10%
        
        # Publisher для уровня батареи
        self.battery_publisher = self.create_publisher(
            Float32,
            '/battery_level',
            10
        )
        
        # Таймер для разрядки батареи (1 Hz)
        self.timer = self.create_timer(1.0, self.update_battery)
        
        self.get_logger().info('Battery Node started - Initial charge: 100%')
    
    def update_battery(self):
        """
        Обновление уровня батареи (вызывается каждую секунду).
        """
        if self.battery_level <= 0.0:
            self.battery_level = 0.0
            # Публикуем 0% если батарея села
            msg = Float32()
            msg.data = self.battery_level
            self.battery_publisher.publish(msg)
            return
        
        # Разрядка на 1% в секунду
        self.battery_level -= 1.0
        
        # Ограничиваем снизу нулем
        if self.battery_level < 0.0:
            self.battery_level = 0.0
        
        # Публикуем текущий уровень
        msg = Float32()
        msg.data = self.battery_level
        self.battery_publisher.publish(msg)
        
        # Логирование каждые 10% снижения
        current_percent = int(self.battery_level)
        
        # Проверяем, пересекли ли мы очередную границу в 10%
        # Логируем при 90%, 80%, 70%, ... 10%, 0%
        if current_percent <= self.last_logged_percent - 10 or current_percent == 0:
            self.last_logged_percent = current_percent
            self.get_logger().info(f'Battery: {int(self.battery_level)}%')


def main(args=None):
    rclpy.init(args=args)
    node = BatteryNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

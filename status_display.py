#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String, Bool


class RobotStatusNode(Node):
    """
    Мониторинг статуса робота на основе данных батареи и дальномера.
    Публикует статус робота с частотой 2 Hz.
    """
    
    def __init__(self):
        super().__init__('robot_status_node')
        
        # Текущие данные от сенсоров
        self.battery_level = 100.0  # начальное значение
        self.distance = 3.0          # начальное значение
        
        # Текущий статус (для отслеживания изменений)
        self.current_status = ""
        
        # Publisher для статуса робота (2 Hz)
        self.status_publisher = self.create_publisher(
            String,
            '/robot_status',
            10
        )
        
        # Subscriber для уровня батареи
        self.battery_subscriber = self.create_subscription(
            Float32,
            '/battery_level',
            self.battery_callback,
            10
        )
        
        # Subscriber для дистанции
        self.distance_subscriber = self.create_subscription(
            Float32,
            '/distance',
            self.distance_callback,
            10
        )
        
        # Таймер для публикации статуса (2 Hz = 0.5 сек)
        self.timer = self.create_timer(0.5, self.publish_status)
        
        self.get_logger().info('Robot Status Node started')
        self.get_logger().info('Monitoring battery and distance sensors')
    
    def battery_callback(self, msg):
        """
        Обновляет текущий уровень батареи.
        """
        self.battery_level = msg.data
    
    def distance_callback(self, msg):
        """
        Обновляет текущее расстояние до препятствия.
        """
        self.distance = msg.data
    
    def determine_status(self):
        """
        Определяет статус робота по текущим показаниям сенсоров.
        Возвращает строку со статусом.
        """
        # Проверяем критические условия (приоритетные)
        if self.battery_level < 10.0 or self.distance < 0.7:
            return "CRITICAL"
        
        # Проверяем предупреждения
        if self.battery_level < 20.0:
            return "WARNING: Low battery"
        
        if self.distance < 1.0:
            return "WARNING: Obstacle close"
        
        # Все хорошо
        if self.battery_level >= 20.0 and self.distance >= 1.0:
            return "ALL OK"
        
        # На всякий случай (если ни одно условие не подошло)
        return "UNKNOWN STATE"
    
    def publish_status(self):
        """
        Публикует статус робота и логирует изменения.
        """
        # Определяем текущий статус
        new_status = self.determine_status()
        
        # Создаем сообщение
        msg = String()
        msg.data = new_status
        
        # Публикуем статус
        self.status_publisher.publish(msg)
        
        # Логируем только если статус изменился
        if new_status != self.current_status:
            if new_status == "CRITICAL":
                self.get_logger().error(f'Status changed to: {new_status}')
            elif "WARNING" in new_status:
                self.get_logger().warn(f'Status changed to: {new_status}')
            else:
                self.get_logger().info(f'Status changed to: {new_status}')
            
            self.current_status = new_status
        
        # Для отладки можно логировать каждую публикацию (раскомментировать при необходимости)
        # self.get_logger().debug(f'Current status: {new_status} (Battery: {self.battery_level:.1f}%, Distance: {self.distance:.2f}m)')


def main(args=None):
    rclpy.init(args=args)
    node = RobotStatusNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

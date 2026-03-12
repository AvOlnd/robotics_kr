#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


class DistanceSensorNode(Node):
    """
    Симулятор дальномера (ультразвукового/лазерного датчика).
    Изменяет показания в зависимости от скорости робота.
    """
    
    def __init__(self):
        super().__init__('distance_sensor_node')
        
        # Параметры дальномера
        self.current_distance = 3.0  # текущее расстояние (начальное)
        self.MIN_DISTANCE = 0.5      # минимальное расстояние (метры)
        self.MAX_DISTANCE = 3.0      # максимальное расстояние (метры)
        self.STEP_CHANGE = 0.2       # изменение за один шаг (метры)
        
        # Текущая скорость робота
        self.current_linear_x = 0.0
        
        # Publisher для дистанции (5 Hz)
        self.distance_publisher = self.create_publisher(
            Float32,
            '/distance',
            10
        )
        
        # Subscriber для скорости робота
        self.cmd_vel_subscriber = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # Таймер для обновления и публикации дистанции (5 Hz = 0.2 сек)
        self.timer = self.create_timer(0.2, self.update_and_publish_distance)
        
        self.get_logger().info('Distance Sensor Node started')
        self.get_logger().info(f'Initial distance: {self.current_distance:.1f}m')
    
    def cmd_vel_callback(self, msg):
        """
        Получаем команды скорости от /cmd_vel.
        Обновляем текущую скорость робота.
        """
        self.current_linear_x = msg.linear.x
        direction = "вперед" if self.current_linear_x > 0 else "назад" if self.current_linear_x < 0 else "стоп"
        self.get_logger().debug(f'Скорость: {direction} ({self.current_linear_x:.2f} м/с)')
    
    def update_and_publish_distance(self):
        """
        Обновляет показания дальномера и публикует их.
        Вызывается каждые 0.2 секунды (5 Hz).
        """
        # Обновляем расстояние в зависимости от скорости
        if self.current_linear_x > 0:  # Движение вперед
            # Уменьшаем расстояние (робот приближается к препятствию)
            self.current_distance -= self.STEP_CHANGE
            self.current_distance = max(self.MIN_DISTANCE, self.current_distance)
            
        elif self.current_linear_x < 0:  # Движение назад
            # Увеличиваем расстояние (робот отдаляется от препятствия)
            self.current_distance += self.STEP_CHANGE
            self.current_distance = min(self.MAX_DISTANCE, self.current_distance)
        
        # Если скорость = 0, расстояние не меняется (остается текущим)
        
        # Публикуем текущее расстояние
        msg = Float32()
        msg.data = self.current_distance
        self.distance_publisher.publish(msg)
        
        # Логируем изменение (каждые 5 обновлений или при изменении)
        self.get_logger().info(f'Distance: {self.current_distance:.2f}m', throttle_duration_sec=1.0)


def main(args=None):
    rclpy.init(args=args)
    node = DistanceSensorNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

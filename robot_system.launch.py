#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launch-файл для запуска всех узлов робота:
    - battery_node
    - distance_sensor
    - status_display (robot_status_node)
    - robot_controller
    - robot_state_publisher с загрузкой URDF
    """
    
    # Получаем путь к директории пакета
    pkg_share = get_package_share_directory('exam_robot')
    
    # Путь к файлу URDF (предполагается, что он лежит в папке urdf пакета)
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf')
    
    # Читаем содержимое URDF файла
    with open(urdf_file, 'r') as infp:
        robot_description_content = infp.read()
    
    # Параметры для robot_state_publisher
    robot_state_publisher_params = {'robot_description': robot_description_content}
    
    # Узел battery_node
    battery_node = Node(
        package='exam_robot',
        executable='battery_node',
        name='battery_node',
        output='screen',
        parameters=[],
        remappings=[]
    )
    
    # Узел distance_sensor
    distance_sensor_node = Node(
        package='exam_robot',
        executable='distance_sensor_node',  # или просто 'distance_sensor' в зависимости от setup.py
        name='distance_sensor',
        output='screen',
        parameters=[],
        remappings=[]
    )
    
    # Узел status_display (robot_status_node)
    status_display_node = Node(
        package='exam_robot',
        executable='robot_status_node',  # или 'status_display' в зависимости от setup.py
        name='status_display',
        output='screen',
        parameters=[],
        remappings=[
            # Если нужно переименовать топики, можно добавить здесь
            # ('/battery_level', '/battery_status'),
            # ('/distance', '/distance_sensor'),
        ]
    )
    
    # Узел robot_controller
    robot_controller_node = Node(
        package='exam_robot',
        executable='robot_controller_node',  # или 'robot_controller' в зависимости от setup.py
        name='robot_controller',
        output='screen',
        parameters=[],
        remappings=[]
    )
    
    # Узел robot_state_publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_state_publisher_params]
    )
    
    # Опционально: узел для визуализации в RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_share, 'config', 'robot_display.rviz')],
        condition=LaunchCondition()  # Можно добавить условие для запуска
    )
    
    # Создаем LaunchDescription и добавляем все узлы
    ld = LaunchDescription()
    
    # Добавляем все узлы
    ld.add_action(battery_node)
    ld.add_action(distance_sensor_node)
    ld.add_action(status_display_node)
    ld.add_action(robot_controller_node)
    ld.add_action(robot_state_publisher_node)
    
    # Можно добавить RViz, если нужно
    # ld.add_action(rviz_node)
    
    return ld

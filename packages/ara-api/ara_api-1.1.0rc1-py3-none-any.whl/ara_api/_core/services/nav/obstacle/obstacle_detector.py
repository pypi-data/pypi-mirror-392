from typing import Dict, List, Tuple

import numpy as np

from ara_api._utils import Rotation, Vector3


class ObstacleDetector:
    """
    Детектор препятствий для локального планировщика.
    Моделирует сенсоры, такие как лидар, сонары или камеры.
    """

    def __init__(
        self,
        max_range: float = 10.0,  # Максимальная дальность обнаружения
        fov: float = 360.0,  # Угол обзора в градусах
        resolution: float = 1.0,
    ):  # Разрешение сканирования
        """
        Инициализация детектора препятствий.

        Args:
            max_range: Максимальная дальность обнаружения (м)
            fov: Угол обзора в градусах
            (по умолчанию 360 - круговой обзор)
            resolution: Разрешение сканирования (м)
        """
        self.max_range = max_range
        self.fov = np.radians(fov)
        self.resolution = resolution

        # Для моделирования сенсоров в симуляции
        self._simulated_obstacles: List[
            Tuple[Vector3, float]
        ] = []  # (центр, радиус)

    def set_simulated_obstacles(self, obstacles: List[Tuple[Vector3, float]]):
        """
        Установка препятствий для симуляции.

        Args:
            obstacles: Список препятствий в виде (центр, радиус)
        """
        self._simulated_obstacles = obstacles

    def scan(
        self, position: Vector3, direction: Rotation
    ) -> Dict[str, List[float]]:
        """
        Сканирование окружения на наличие препятствий.

        Args:
            position: Текущая позиция дрона
            direction: Текущее направление дрона

        Returns:
            Словарь с данными сканирования:
                'angles': углы сканирования (рад)
                'distances': расстояния до препятствий (м)
        """
        # Для реальной системы здесь был бы код работы с сенсорами
        # В симуляции моделируем лидарное сканирование

        # Количество лучей для сканирования
        num_rays = int(np.ceil(2 * np.pi * self.resolution / self.max_range))
        angles = np.linspace(-self.fov / 2, self.fov / 2, num_rays)
        distances = np.full_like(angles, self.max_range)

        # Применяем поворот
        if hasattr(direction, "rotation"):
            rotation_matrix = direction.rotation.as_matrix()
            # Для каждого луча
            for i, angle in enumerate(angles):
                # Вычисляем направление луча
                ray_local = np.array([np.cos(angle), np.sin(angle), 0.0])
                ray = rotation_matrix.dot(ray_local)

                # Проверяем пересечение с препятствиями
                for (
                    obstacle_center,
                    obstacle_radius,
                ) in self._simulated_obstacles:
                    # Простая проверка пересечения луча со сферой
                    obstacle_pos = np.array(
                        [
                            obstacle_center.x,
                            obstacle_center.y,
                            obstacle_center.z,
                        ]
                    )
                    drone_pos = np.array([position.x, position.y, position.z])

                    # Вектор от дрона к центру препятствия
                    drone_to_obstacle = obstacle_pos - drone_pos

                    # Проекция этого вектора на луч
                    projection = np.dot(drone_to_obstacle, ray)

                    # Если препятствие находится за дроном, пропускаем
                    if projection < 0:
                        continue

                    # Находим ближайшую точку от луча
                    # до центра препятствия
                    closest_point = drone_pos + ray * projection
                    distance_to_center = np.linalg.norm(
                        closest_point - obstacle_pos
                    )

                    # Если луч проходит близко к центру препятствия
                    # (касается или пересекает его)
                    if distance_to_center <= obstacle_radius:
                        # Расчет расстояния до точки пересечения
                        dx = np.sqrt(
                            obstacle_radius**2 - distance_to_center**2
                        )
                        intersection_distance = projection - dx

                        # Обновляем расстояние,
                        # если это ближайшее препятствие
                        if 0 < intersection_distance < distances[i]:
                            distances[i] = intersection_distance

        return {"angles": angles.tolist(), "distances": distances.tolist()}

"""Obstacle map for path planning"""

from typing import List, Tuple, Union

from ara_api._utils.data.nav.obstacle_box import ObstacleBox
from ara_api._utils.data.nav.vector3 import Vector3


class ObstacleMap:
    """Карта препятствий для планирования траектории."""

    def __init__(
        self,
        obstacles: List[
            Union[ObstacleBox, Tuple[float, float, float, float, float, float]]
        ] = None,
    ):
        """
        Инициализация карты препятствий.

        Args:
            obstacles: Список препятствий, может быть ObstacleBox или
                       кортеж (x_min, y_min, z_min, x_max, y_max, z_max)
        """
        self.obstacles: List[ObstacleBox] = []

        if obstacles:
            for obstacle in obstacles:
                if isinstance(obstacle, ObstacleBox):
                    self.obstacles.append(obstacle)
                elif isinstance(obstacle, tuple) and len(obstacle) == 6:
                    self.obstacles.append(ObstacleBox.from_tuple(obstacle))
                else:
                    raise ValueError(
                        f"Неизвестный тип препятствия: {type(obstacle)}"
                    )

    def add_obstacle(
        self,
        obstacle: Union[
            ObstacleBox, Tuple[float, float, float, float, float, float]
        ],
    ):
        """
        Добавить препятствие на карту.

        Args:
            obstacle: Препятствие в виде ObstacleBox или кортежа
                      (x_min, y_min, z_min, x_max, y_max, z_max)
        """
        if isinstance(obstacle, ObstacleBox):
            self.obstacles.append(obstacle)
        elif isinstance(obstacle, tuple) and len(obstacle) == 6:
            self.obstacles.append(ObstacleBox.from_tuple(obstacle))
        else:
            raise ValueError(f"Неизвестный тип препятствия: {type(obstacle)}")

    def is_collision(self, point: Vector3, safety_margin: float = 0.5) -> bool:
        """
        Проверить, находится ли точка внутри какого-либо препятствия
        (с отступом).

        Args:
            point: Точка для проверки
            safety_margin: Дополнительный отступ безопасности

        Returns:
            True если точка находится внутри или вблизи препятствия,
            False иначе
        """
        for obstacle in self.obstacles:
            if obstacle.contains_point(point, safety_margin):
                return True
        return False

    def is_path_clear(
        self,
        start: Vector3,
        end: Vector3,
        safety_margin: float = 0.5,
        check_points: int = 10,
    ) -> bool:
        """
        Проверить, свободен ли путь между двумя точками от препятствий.

        Args:
            start: Начальная точка
            end: Конечная точка
            safety_margin: Отступ безопасности
            check_points: Количество промежуточных точек для проверки

        Returns:
            True если путь свободен, False иначе
        """
        # Проверяем промежуточные точки на прямой между start и end
        for i in range(check_points + 1):
            t = i / check_points
            point = Vector3(
                start.x + t * (end.x - start.x),
                start.y + t * (end.y - start.y),
                start.z + t * (end.z - start.z),
            )
            if self.is_collision(point, safety_margin):
                return False

        return True

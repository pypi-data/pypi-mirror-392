"""Obstacle box data class for 3D obstacles"""

from dataclasses import dataclass
from typing import Tuple

from ara_api._utils.data.nav.vector3 import Vector3


@dataclass
class ObstacleBox:
    """Препятствие в виде параллелепипеда в 3D пространстве."""

    min_point: Vector3
    max_point: Vector3

    @property
    def center(self) -> Vector3:
        """Получить центр препятствия."""
        return Vector3(
            (self.min_point.x + self.max_point.x) / 2,
            (self.min_point.y + self.max_point.y) / 2,
            (self.min_point.z + self.max_point.z) / 2,
        )

    @property
    def dimensions(self) -> Vector3:
        """Получить размеры препятствия по осям."""
        return Vector3(
            abs(self.max_point.x - self.min_point.x),
            abs(self.max_point.y - self.min_point.y),
            abs(self.max_point.z - self.min_point.z),
        )

    def contains_point(
        self, point: Vector3, safety_margin: float = 0.0
    ) -> bool:
        """
        Проверить, находится ли точка внутри препятствия (с отступом).
        """
        return (
            self.min_point.x - safety_margin
            <= point.x
            <= self.max_point.x + safety_margin
            and self.min_point.y - safety_margin
            <= point.y
            <= self.max_point.y + safety_margin
            and self.min_point.z - safety_margin
            <= point.z
            <= self.max_point.z + safety_margin
        )

    @classmethod
    def from_tuple(
        cls, box_tuple: Tuple[float, float, float, float, float, float]
    ) -> "ObstacleBox":
        """
        Создать препятствие из кортежа
        (x_min, y_min, z_min, x_max, y_max, z_max).
        """
        x_min, y_min, z_min, x_max, y_max, z_max = box_tuple
        return cls(
            min_point=Vector3(x_min, y_min, z_min),
            max_point=Vector3(x_max, y_max, z_max),
        )

    def __repr__(self):
        return (
            "ObstacleBox(min_point={min_point}, max_point={max_point}, "
            "center={center}, dimensions={dimensions})".format(
                min_point=self.min_point,
                max_point=self.max_point,
                center=self.center,
                dimensions=self.dimensions,
            )
        )

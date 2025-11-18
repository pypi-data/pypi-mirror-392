"""Base planner abstract class"""

from abc import ABC, abstractmethod

from ara_api._utils.data.nav.obstacle_map import ObstacleMap
from ara_api._utils.data.nav.path import Path
from ara_api._utils.data.nav.vector3 import Vector3


class BasePlanner(ABC):
    @abstractmethod
    def plan(
        self, start: Vector3, end: Vector3, obstacle: ObstacleMap
    ) -> Path: ...

import math
from dataclasses import replace
from typing import Any, Dict, Tuple

from ara_api._utils import GoalStatistic, GoalStatus, Point3D
from ara_api._utils.config import GOAL_CHECKER


class SimpleGoalChecker:
    """
    Проверяет достижение целевой точки дроном.

    Реализует функциональность аналогичную nav2_goal_checker из ROS2:
    - Проверка позиции по X, Y, Z координатам с настраиваемыми допусками
    - Проверка ориентации по YAW углу
    - Селективные проверки (можно отключить Z или YAW)
    - Детальная диагностика и статистика

    Attributes:
        _logger: Логгер для диагностических сообщений.
        _xy_goal_tolerance: Допуск по XY координатам (м).
        _z_goal_tolerance: Допуск по Z координате (м).
        _yaw_goal_tolerance: Допуск по YAW углу (рад).
        _check_z: Флаг проверки Z координаты.
        _check_yaw: Флаг проверки YAW угла.
        _stats: Статистика проверок.
    """

    def __init__(self) -> None:
        """
        Инициализирует проверщик достижения цели.

        Args:
            xy_goal_tolerance: Допуск по XY координатам в метрах.
            z_goal_tolerance: Допуск по Z координате в метрах.
            yaw_goal_tolerance: Допуск по YAW углу в радианах.
            check_z: Включить проверку Z координаты.
            check_yaw: Включить проверку YAW угла.
        """
        # self._logger = logging.getLogger(__name__)

        self._stats = GoalStatistic()

    def is_goal_reached(
        self, current_pose: Point3D, goal_pose: Point3D
    ) -> bool:
        """
        Проверяет, достигнута ли целевая точка.

        Args:
            current_pose: Текущая позиция и ориентация дрона.
            goal_pose: Целевая позиция и ориентация.

        Returns:
            True если цель достигнута, False иначе.
        """
        status = self._calculate_goal_status(current_pose, goal_pose)
        self._stats.update(status)

        return status.is_reached

    def get_distance_to_goal(
        self, current_pose: Point3D, goal_pose: Point3D
    ) -> Tuple[float, float, float]:
        """
        Вычисляет расстояние до цели.

        Args:
            current_pose: Текущая позиция и ориентация дрона.
            goal_pose: Целевая позиция и ориентация.

        Returns:
            Кортеж (distance_xy, distance_z, yaw_diff) в
            метрах и радианах.
        """
        dx = goal_pose.position.x - current_pose.position.x
        dy = goal_pose.position.y - current_pose.position.y
        distance_xy = math.sqrt(dx * dx + dy * dy)

        distance_z = abs(goal_pose.position.z - current_pose.position.z)

        yaw_diff = self._normalize_angle_diff(goal_pose.yaw - current_pose.yaw)

        return distance_xy, distance_z, abs(yaw_diff)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику работы проверщика.

        Returns:
            Словарь со статистическими данными.
        """
        stats = replace(self._stats)

        if stats.total_checks > 0:
            stats.success_rate = stats.goals_reached / stats.total_checks
            stats.position_success_rate = (
                stats.position_reached_count / stats.total_checks
            )
            if GOAL_CHECKER.CHECK_YAW:
                stats.yaw_success_rate = (
                    stats.yaw_reached_count / stats.total_checks
                )
        else:
            stats.success_rate = 0.0
            stats.position_success_rate = 0.0
            stats.yaw_success_rate = 0.0

        return stats

    def reset_statistics(self) -> None:
        """
        Сбрасывает статистику проверок.

        Используется для очистки данных перед новой серией проверок.
        """
        self._stats.reset()
        # self._logger.info("Статистика проверок сброшена.")

    def _calculate_goal_status(
        self, current_pose: Point3D, goal_pose: Point3D
    ) -> GoalStatus:
        """
        Вычисляет статус достижения цели.

        Args:
            current_pose: Текущая позиция и ориентация.
            goal_pose: Целевая позиция и ориентация.

        Returns:
            Объект GoalStatus с результатами проверки.
        """
        status = GoalStatus()

        status.distance_xy, status.distance_z, status.yaw_diff = (
            self.get_distance_to_goal(current_pose, goal_pose)
        )

        xy_reached = status.distance_xy <= GOAL_CHECKER.XY_GOAL_TOLERANCE
        z_reached = True

        if GOAL_CHECKER.CHECK_Z:
            z_reached = status.distance_z <= GOAL_CHECKER.Z_GOAL_TOLERANCE

        status.position_reached = xy_reached and z_reached

        if GOAL_CHECKER.CHECK_YAW:
            status.yaw_reached = (
                status.yaw_diff <= GOAL_CHECKER.YAW_GOAL_TOLERANCE
            )
        else:
            status.yaw_reached = True

        status.is_reached = status.position_reached and status.yaw_reached

        return status

    def _normalize_angle_diff(self, angle_diff: float) -> float:
        """
        Нормализует разность углов в диапазон [-π, π].

        Args:
            angle_diff: Разность углов в радианах.

        Returns:
            Нормализованная разность углов.
        """
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        return angle_diff

from typing import List, Tuple, Union

from ara_api._core.services.nav.checker import SimpleGoalChecker
from ara_api._core.services.nav.planner.algorithms import (
    AStarPlanner,
    CarrotPlanner,
    RRTStarPlanner,
)
from ara_api._core.services.nav.smoother import SimpleSmoother
from ara_api._utils import (
    ObstacleBox,
    ObstacleMap,
    Path,
    PlanningAlgorithm,
    Vector3,
)
from ara_api._utils.config import GLOBAL, OBSTACLE_MAP


class GlobalNavigationPlanner:
    def __init__(self):
        """
        Инициализирует планировщик глобальной навигации.
        """
        self.smoother = SimpleSmoother()
        self.goal_checker = SimpleGoalChecker()

        if GLOBAL.ALGORITHM == PlanningAlgorithm.A_STAR:
            self.algorithm = AStarPlanner()
        elif GLOBAL.ALGORITHM == PlanningAlgorithm.RRT_STAR:
            self.algorithm = RRTStarPlanner()
        elif GLOBAL.ALGORITHM == PlanningAlgorithm.CARROT:
            self.algorithm = CarrotPlanner()
        else:
            raise Exception(
                f"Неподдерживаемый алгоритм планирования: {GLOBAL.ALGORITHM}"
            )

    def plan_path(
        self,
        start: Vector3,
        goal: Vector3,
        obstacles: Union[
            List[ObstacleBox],
            List[Tuple[float, float, float, float, float, float]],
        ],
    ) -> Path:
        """
        Планирует путь от начальной до целевой точки.

        Args:
            start: Начальная точка
            goal: Целевая точка
            obstacles: Список препятствий
            algorithm: Алгоритм планирования
            enable_smoothing: Включить сглаживание траектории
            smoothing_iterations: Количество итераций сглаживания

        Returns:
            Спланированная траектория

        Raises:
            Exception: Если планирование невозможно
        """
        obstacle_map = ObstacleMap(obstacles)

        if obstacle_map.is_collision(start, OBSTACLE_MAP.SAFETY_MARGIN):
            raise Exception("Start position is in collision with an obstacle.")

        if obstacle_map.is_collision(goal, OBSTACLE_MAP.SAFETY_MARGIN):
            raise Exception("Goal position is in collision with an obstacle.")

        path = self.algorithm.plan(
            start=start, goal=goal, obstacle_map=obstacle_map
        )

        if GLOBAL.SMOOTH_PATH and len(path.segments) > 1:
            try:
                obstacle_boxes = []
                if isinstance(obstacles, list) and obstacles:
                    if isinstance(obstacles[0], ObstacleBox):
                        obstacle_boxes = obstacles
                    else:
                        for obs in obstacles:
                            if len(obs) == 6:
                                obstacle_boxes.append(
                                    ObstacleBox(
                                        min_point=Vector3(
                                            obs[0], obs[1], obs[2]
                                        ),
                                        max_point=Vector3(
                                            obs[3], obs[4], obs[5]
                                        ),
                                    )
                                )

                smoothed_path = self.smoother.smooth_path(
                    path,
                    obstacles=obstacle_boxes,
                )

                return smoothed_path

            except Exception as e:
                print(
                    f"Ошибка сглаживания: {e}. Возвращаем исходную траекторию."
                )
                return path

        return path

    def check_goal_reached(
        self,
        current_position: Vector3,
        goal_position: Vector3,
        current_yaw: float = 0.0,
        goal_yaw: float = 0.0,
    ) -> tuple:
        """
        Проверяет достижение цели с помощью SimpleGoalChecker.

        Args:
            current_position: Текущая позиция дрона
            goal_position: Целевая позиция
            current_yaw: Текущий угол рыскания (радианы)
            goal_yaw: Целевой угол рыскания (радианы)

        Returns:
            Кортеж (достигнута_ли_цель, подробный_статус)
        """
        from ara_api._core.services.nav.checker import Point3D

        current_point = Point3D(
            x=current_position.x,
            y=current_position.y,
            z=current_position.z,
            yaw=current_yaw,
        )

        goal_point = Point3D(
            x=goal_position.x,
            y=goal_position.y,
            z=goal_position.z,
            yaw=goal_yaw,
        )

        # Получаем полный статус
        status = self.goal_checker.get_goal_status_info(
            current_point, goal_point
        )
        is_reached = self.goal_checker.is_goal_reached(
            current_point, goal_point
        )

        return is_reached, status

    def get_goal_checker_stats(self) -> dict:
        """
        Возвращает статистику проверок цели.

        Returns:
            Словарь со статистикой SimpleGoalChecker
        """
        return self.goal_checker.get_statistics()

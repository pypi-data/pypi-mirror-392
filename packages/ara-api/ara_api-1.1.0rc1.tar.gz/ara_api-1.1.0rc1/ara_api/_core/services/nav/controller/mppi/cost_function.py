import logging
import math
from typing import List, Optional

import numpy as np

from ara_api._utils import (
    MPPIState,
    MPPITrajectory,
    ObstacleBox,
    Path,
    Vector3,
)
from ara_api._utils.config import MPPI


class MPPICostFunction:
    """
    Функция стоимости для MPPI контроллера.

    Вычисляет стоимость траектории на основе нескольких критериев:
    - Отслеживание заданного пути
    - Избегание препятствий
    - Плавность управления
    - Достижение цели
    """

    def __init__(
        self,
        obstacles: List[ObstacleBox],
        noise_covariance: np.ndarray,
        temperature: float,
    ):
        """
        Инициализация функции стоимости.

        Args:
            obstacles: Список препятствий в рабочем пространстве.
        """
        self.update_obstacles(obstacles)
        self._logger = logging.getLogger(__name__)

        try:
            inv_covariance = np.linalg.inv(noise_covariance)
            self._control_cost_matrix = temperature * inv_covariance
        except np.linalg.LinAlgError as e:
            self._logger.error(
                "Матрица ковариации шума вырождена."
                " Используется единичная матрица"
            )
            self._control_cost_matrix = temperature * np.eye(
                noise_covariance.shape[0]
            )

    def compute_trajectory_cost(
        self,
        trajectory: np.ndarray,
        control: np.ndarray,
        reference_path: Optional[Path],
        goal_state: MPPIState,
    ) -> np.ndarray:
        """
        Вычисляет общую стоимость траектории.

        Args:
            trajectory: Сэмплированная траектория.
            reference_path: Референсная траектория для отслеживания
                            (может быть None).
            goal_state: Целевое состояние.

        Returns:
            Общая стоимость траектории.
        """
        path_cost = self._compute_path_tracking_cost(
            trajectory, reference_path
        )
        obstacle_cost = self._compute_obstacle_avoidance_cost(trajectory)
        control_cost = self._compute_control_cost(control)
        goal_cost = self._compute_goal_cost(trajectory, goal_state)

        total_cost = (
            MPPI.PATH_TRACKING_WEIGHT * path_cost
            + MPPI.OBSTACLE_AVOIDANCE_WEIGHT * obstacle_cost
            + MPPI.CONTROL_PENALTY_WEIGHT * control_cost
            + MPPI.GOAL_WEIGHT * goal_cost
        )

        return total_cost

    def _compute_path_tracking_cost(
        self, trajectory: np.ndarray, reference_path: Optional[Path]
    ) -> np.ndarray:
        """
        Вычисляет стоимость отслеживания пути с улучшенным алгоритмом.
        """
        num_samples, horizon, _ = trajectory.shape
        if reference_path is None or not reference_path.segments:
            return np.zeros(num_samples)

        path_starts = np.array(
            [
                [s.start.x, s.start.y, s.start.z]
                for s in reference_path.segments
            ]
        )
        path_ends = np.array(
            [[s.end.x, s.end.y, s.end.z] for s in reference_path.segments]
        )
        path_vectors = path_ends - path_starts
        segment_lengths = np.linalg.norm(path_vectors, axis=1)

        valid_segments = segment_lengths > 1e-6
        if not np.any(valid_segments):
            self._logger.warning("All path segments are too short.")
            return np.zeros(num_samples)

        path_starts = path_starts[valid_segments]
        path_vectors = path_vectors[valid_segments]
        segment_lengths = segment_lengths[valid_segments]
        num_segments = len(path_starts)

        traj_points = trajectory[:, :, :3]  # Извлекаем только позиции

        dist_to_starts = np.linalg.norm(
            traj_points[:, :, np.newaxis, :] - path_starts,
            axis=3,
        )
        closest_segment_indices = np.argmin(dist_to_starts, axis=2)
        target_segment_idx = np.max(closest_segment_indices, axis=1)

        active_path_starts = path_starts[target_segment_idx]
        active_path_ends = path_ends[target_segment_idx]
        active_path_vectors = path_vectors[target_segment_idx]
        active_segment_length = segment_lengths[target_segment_idx]

        vec_to_point = traj_points - active_path_starts[:, np.newaxis, :]

        t = (
            np.einsum("ijk, ik->ij", vec_to_point, active_path_vectors)
            / (active_segment_length**2)[:, np.newaxis]
        )
        t_clamped = np.clip(t, 0, 1)

        closest_points_on_line = (
            active_path_starts[:, np.newaxis, :] + t_clamped[:, :, np.newaxis]
        )

        cross_track_error = np.linalg.norm(
            traj_points - closest_points_on_line, axis=2
        )

        along_track_error = np.linalg.norm(
            active_path_starts[:, np.newaxis, :] - closest_points_on_line,
            axis=2,
        )

        total_path_cost = np.sum(
            cross_track_error**2 + 0.5 * along_track_error**2, axis=1
        )

        return total_path_cost / horizon
        # num_samples = trajectory.shape[0]
        # if reference_path is None or not reference_path.segments:
        #     return np.zeros(num_samples)

        # path_starts = np.array(
        #     [
        #         [s.start.x, s.start.y, s.start.z]
        #         for s in reference_path.segments
        #     ]
        # )
        # path_ends = np.array(
        #     [[s.end.x, s.end.y, s.end.z] for s in reference_path.segments]
        # )

        # path_vectors = path_ends - path_starts
        # segment_lengths_sq = np.sum(path_vectors**2, axis=1)

        # valid_segments = segment_lengths_sq > 1e-6
        # if not np.any(valid_segments):
        #     self._logger.warning("All path segments are too short.")
        #     return np.zeros(num_samples)

        # path_starts = path_starts[valid_segments]
        # path_vectors = path_vectors[valid_segments]
        # segment_lengths_sq = segment_lengths_sq[valid_segments]

        # traj_points = trajectory[:, :, :3]  # Извлекаем только позиции
        # vec_traj_to_start = traj_points[:, :, np.newaxis, :] - path_starts

        # t = (
        #     np.sum((vec_traj_to_start * path_vectors), axis=3)
        #     / segment_lengths_sq
        # )
        # t = np.clip(t, 0, 1)

        # closest_points = path_starts + t[..., np.newaxis] * path_vectors

        # distances_to_segment = np.linalg.norm(
        #     traj_points[:, :, np.newaxis, :] - closest_points, axis=3
        # )

        # min_distances = np.min(distances_to_segment, axis=2)

        # total_error = np.sum(min_distances**2, axis=1)

        # return total_error / trajectory.shape[1]

    def _compute_obstacle_avoidance_cost(
        self, trajectory: np.ndarray
    ) -> np.ndarray:
        """Вычисляет стоимость избегания препятствий."""
        num_samples = trajectory.shape[0]
        if self._obstacles_min.shape[0] == 0:
            return np.zeros(num_samples)

        collision_radius = MPPI.COLLISION_RADIUS + MPPI.SAFETY_MARGIN
        traj_points = trajectory[:, :, :3]

        traj_points_exp = traj_points[:, :, np.newaxis, :]
        obs_min_exp = self._obstacles_min[np.newaxis, np.newaxis, :, :]
        obs_max_exp = self._obstacles_max[np.newaxis, np.newaxis, :, :]

        closest_points = np.clip(traj_points_exp, obs_min_exp, obs_max_exp)

        distances = np.linalg.norm(traj_points_exp - closest_points, axis=3)

        penalty = np.maximum(0, collision_radius - distances)

        total_cost = np.sum(penalty, axis=(1, 2))
        return total_cost

    def _compute_smoothness_cost(self, control: np.ndarray) -> np.ndarray:
        """Вычисляет стоимость плавности управления."""
        control_diff = np.diff(control, axis=1)
        smoothness_cost = np.sum(np.sum(control_diff**2, axis=2), axis=1)
        return smoothness_cost

    def _compute_goal_cost(
        self, trajectory: np.ndarray, goal_state: MPPIState
    ) -> np.ndarray:
        """Вычисляет стоимость достижения цели."""
        final_position = trajectory[:, -1, :3]
        goal_position = np.array(
            [
                goal_state.position.x,
                goal_state.position.y,
                goal_state.position.z,
            ]
        )
        dist_sq = np.sum((final_position - goal_position) ** 2, axis=1)
        return dist_sq

    def _compute_control_cost(self, controls: np.ndarray) -> np.ndarray:
        temp = controls @ self._control_cost_matrix

        cost_per_step = np.sum(controls * temp, axis=2)

        total_control_cost = np.sum(cost_per_step, axis=1)

        return total_control_cost

    def update_obstacles(self, obstacles: List[ObstacleBox]) -> None:
        if not obstacles:
            self._obstacles_min = np.empty((0, 3))
            self._obstacles_max = np.empty((0, 3))
        else:
            self._obstacles_min = np.array(
                [
                    [o.min_point.x, o.min_point.y, o.min_point.z]
                    for o in obstacles
                ]
            )
            self._obstacles_max = np.array(
                [
                    [o.max_point.x, o.max_point.y, o.max_point.z]
                    for o in obstacles
                ]
            )

    def _distance_3d(self, p1: Vector3, p2: Vector3) -> float:
        """Вычисляет 3D расстояние между двумя точками."""
        return math.sqrt(
            (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2
        )

    def _distance_to_obstacle(
        self, position: Vector3, obstacle: ObstacleBox
    ) -> float:
        """Вычисляет минимальное расстояние от точки до препятствия."""
        # Проекция точки на боундинг бокс препятствия
        closest_point = Vector3(
            max(obstacle.min_point.x, min(position.x, obstacle.max_point.x)),
            max(obstacle.min_point.y, min(position.y, obstacle.max_point.y)),
            max(obstacle.min_point.z, min(position.z, obstacle.max_point.z)),
        )

        return self._distance_3d(position, closest_point)

    def _normalize_angle(self, angle: float) -> float:
        """Нормализует угол в диапазон [-π, π]."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

#!/usr/bin/env python3
from typing import List, Optional

import numpy as np

from ara_api._utils import (
    ObstacleBox,
    Path,
    PathSegment,
    Rotation,
    Vector3,
)
from ara_api._utils.config import SMOOTHER


class SimpleSmoother:
    """
    Простой сглаживатель траектории, аналогичный nav2_smoother из ROS2.

    Реализует следующие алгоритмы сглаживания:
    1. Moving Average - усреднение позиций соседних точек
    2. Angular Smoothing - сглаживание резких поворотов
    3. Velocity Smoothing - обеспечение плавных переходов скорости
    4. Adaptive Smoothing - адаптивное сглаживание в зависимости
                            от геометрии пути
    """

    def __init__(self):
        """
        Инициализация сглаживателя.
        """
        pass

    def smooth_path(
        self, path: Path, obstacles: Optional[List[ObstacleBox]] = None
    ) -> Path:
        """
        Основная функция сглаживания траектории.

        Args:
            path: Исходная траектория для сглаживания
            obstacles: Список препятствий для проверки безопасности

        Returns:
            Сглаженная траектория

        Raises:
            Exception: Если траектория пуста или некорректна
        """
        if not path.segments:
            raise Exception("Пустая траектория для сглаживания")

        if len(path.segments) < 2:
            return path

        waypoints = self._extract_waypoints(path)

        smoothed_waypoints = waypoints.copy()

        for iteration in range(SMOOTHER.MAX_ITTERATIONS):
            smoothed_waypoints = self._apply_moving_average(smoothed_waypoints)

            if SMOOTHER.ANGULAR_SMOOTHING_FACTOR > 0:
                smoothed_waypoints = self._smooth_angles(smoothed_waypoints)

            if SMOOTHER.ADAPTIVE_SMOOTHING:
                smoothed_waypoints = self._adaptive_corner_smoothing(
                    smoothed_waypoints
                )

            if obstacles:
                smoothed_waypoints = self._ensure_collision_free(
                    smoothed_waypoints, obstacles
                )

        smoothed_waypoints = self._normalize_segment_lengths(
            smoothed_waypoints
        )

        smoothed_path = self._create_path_from_waypoints(smoothed_waypoints)

        return smoothed_path

    def _extract_waypoints(self, path: Path) -> List[Vector3]:
        """
        Извлекает путевые точки из траектории.

        Args:
            path: Исходная траектория

        Returns:
            Список путевых точек
        """
        waypoints = []

        if path.segments:
            # Добавляем начальную точку первого сегмента
            waypoints.append(path.segments[0].start)

            # Добавляем конечные точки всех сегментов
            for segment in path.segments:
                waypoints.append(segment.end)

        return waypoints

    def _apply_moving_average(self, waypoints: List[Vector3]) -> List[Vector3]:
        """
        Применяет Moving Average сглаживание к путевым точкам.

        Args:
            waypoints: Исходные путевые точки

        Returns:
            Сглаженные путевые точки
        """
        if len(waypoints) < 3:
            return waypoints

        smoothed = waypoints.copy()
        window_size = min(SMOOTHER.WINDOW_SIZE, len(waypoints))
        half_window = window_size // 2

        # Применяем сглаживание к внутренним точкам
        # (не трогаем начало и конец)
        for i in range(half_window, len(waypoints) - half_window):
            avg_x = 0.0
            avg_y = 0.0
            avg_z = 0.0

            # Усредняем позиции в окне
            for j in range(i - half_window, i + half_window + 1):
                avg_x += waypoints[j].x
                avg_y += waypoints[j].y
                avg_z += waypoints[j].z

            count = 2 * half_window + 1
            smoothed[i] = Vector3(
                x=avg_x / count, y=avg_y / count, z=avg_z / count
            )

        return smoothed

    def _smooth_angles(self, waypoints: List[Vector3]) -> List[Vector3]:
        """
        Сглаживает резкие изменения направления движения.

        Args:
            waypoints: Исходные путевые точки

        Returns:
            Точки с сглаженными углами
        """
        if len(waypoints) < 3:
            return waypoints

        smoothed = waypoints.copy()
        factor = SMOOTHER.ANGULAR_SMOOTHING_FACTOR

        for i in range(1, len(waypoints) - 1):
            prev_point = waypoints[i - 1]
            curr_point = waypoints[i]
            next_point = waypoints[i + 1]

            angle = self._detect_corner_severity(
                prev_point, curr_point, next_point
            )

            # Если угол слишком резкий, сглаживаем
            if angle > SMOOTHER.MAX_ANGULAR_CHANGE:
                # Интерполируем позицию для более плавного поворота
                smoothed[i] = Vector3(
                    x=curr_point.x
                    + factor
                    * (prev_point.x + next_point.x - 2 * curr_point.x)
                    / 2,
                    y=curr_point.y
                    + factor
                    * (prev_point.y + next_point.y - 2 * curr_point.y)
                    / 2,
                    z=curr_point.z
                    + factor
                    * (prev_point.z + next_point.z - 2 * curr_point.z)
                    / 2,
                )

        return smoothed

    def _adaptive_corner_smoothing(
        self, waypoints: List[Vector3]
    ) -> List[Vector3]:
        """
        Применяет адаптивное сглаживание в зависимости от геометрии
        поворотов.

        Args:
            waypoints: Исходные путевые точки

        Returns:
            Адаптивно сглаженные точки
        """
        if len(waypoints) < 3:
            return waypoints

        smoothed = waypoints.copy()

        for i in range(1, len(waypoints) - 1):
            prev_point = waypoints[i - 1]
            curr_point = waypoints[i]
            next_point = waypoints[i + 1]

            # Обнаруживаем повороты
            corner_severity = self._detect_corner_severity(
                prev_point, curr_point, next_point
            )

            if corner_severity > SMOOTHER.CORNER_DETECTION_THRESHHOLD:
                # Применяем более агрессивное сглаживание
                # для резких поворотов
                smoothing_factor = min(0.5, corner_severity / np.pi)

                smoothed[i] = Vector3(
                    x=curr_point.x
                    + smoothing_factor
                    * (prev_point.x + next_point.x - 2 * curr_point.x)
                    / 2,
                    y=curr_point.y
                    + smoothing_factor
                    * (prev_point.y + next_point.y - 2 * curr_point.y)
                    / 2,
                    z=curr_point.z
                    + smoothing_factor
                    * (prev_point.z + next_point.z - 2 * curr_point.z)
                    / 2,
                )

        return smoothed

    def _ensure_collision_free(
        self, waypoints: List[Vector3], obstacles: List[ObstacleBox]
    ) -> List[Vector3]:
        """
        Обеспечивает отсутствие коллизий сглаженной траектории.

        Args:
            waypoints: Сглаженные путевые точки
            obstacles: Список препятствий

        Returns:
            Безопасные путевые точки
        """
        safe_waypoints = waypoints.copy()

        for i, waypoint in enumerate(waypoints):
            # Проверяем коллизии с препятствиями
            if self._is_point_in_collision(waypoint, obstacles):
                # Если точка в коллизии, возвращаем к исходной позиции
                # или ищем ближайшую безопасную позицию
                safe_waypoints[i] = self._find_nearest_safe_point(
                    waypoint,
                    obstacles,
                    waypoints[max(0, i - 1)] if i > 0 else waypoint,
                )

        return safe_waypoints

    def _normalize_segment_lengths(
        self, waypoints: List[Vector3]
    ) -> List[Vector3]:
        """
        Нормализует длины сегментов траектории.

        Args:
            waypoints: Путевые точки

        Returns:
            Точки с нормализованными сегментами
        """
        if len(waypoints) < 2:
            return waypoints

        normalized = [waypoints[0]]  # Начальная точка остается неизменной

        for i in range(1, len(waypoints)):
            prev_point = normalized[-1]
            curr_point = waypoints[i]

            # Вычисляем расстояние между точками
            distance = self._distance_3d(prev_point, curr_point)

            if distance < SMOOTHER.MIN_SEGMENT_LENGHT:
                # Сегмент слишком короткий - пропускаем точку
                continue
            elif distance > SMOOTHER.MAX_SEGMENT_LENGHT:
                # Сегмент слишком длинный - добавляем
                # промежуточные точки
                num_segments = int(
                    np.ceil(distance / SMOOTHER.MAX_SEGMENT_LENGHT)
                )

                for j in range(1, num_segments + 1):
                    ratio = j / num_segments
                    intermediate_point = Vector3(
                        x=prev_point.x + ratio * (curr_point.x - prev_point.x),
                        y=prev_point.y + ratio * (curr_point.y - prev_point.y),
                        z=prev_point.z + ratio * (curr_point.z - prev_point.z),
                    )
                    normalized.append(intermediate_point)
            else:
                # Сегмент нормальной длины
                normalized.append(curr_point)

        return normalized

    def _create_path_from_waypoints(self, waypoints: List[Vector3]) -> Path:
        """
        Создает объект Path из списка путевых точек.

        Args:
            waypoints: Путевые точки

        Returns:
            Объект траектории
        """
        if len(waypoints) < 2:
            raise Exception("Недостаточно точек для создания траектории")

        path = Path()

        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i + 1]

            # Вычисляем ориентацию на основе направления движения
            start_heading = self._compute_heading(start, end)
            end_heading = start_heading  # Упрощенная версия

            segment = PathSegment(
                start=start,
                end=end,
                start_heading=start_heading,
                end_heading=end_heading,
                metadata={
                    "index": i,
                    "smoother": "simple_smoother",
                    "smoothed": True,
                },
            )

            path.add_segment(segment)

        return path

    def _angle_between_vectors(self, vec1: Vector3, vec2: Vector3) -> float:
        """Вычисляет угол между двумя векторами."""
        mag1 = vec1.magnitude
        mag2 = vec2.magnitude

        if mag1 < 1e-6 or mag2 < 1e-6:
            return 0.0

        dot_product = vec1.x * vec2.x + vec1.y * vec2.y + vec1.z * vec2.z
        cos_angle = np.clip(dot_product / (mag1 * mag2), -1.0, 1.0)

        return np.arccos(cos_angle)

    def _detect_corner_severity(
        self, prev_point: Vector3, curr_point: Vector3, next_point: Vector3
    ) -> float:
        """Определяет степень резкости поворота."""
        vec1 = Vector3(
            curr_point.x - prev_point.x,
            curr_point.y - prev_point.y,
            curr_point.z - prev_point.z,
        )

        vec2 = Vector3(
            next_point.x - curr_point.x,
            next_point.y - curr_point.y,
            next_point.z - curr_point.z,
        )

        return self._angle_between_vectors(vec1, vec2)

    def _distance_3d(self, p1: Vector3, p2: Vector3) -> float:
        """Вычисляет 3D расстояние между точками."""
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dz = p2.z - p1.z
        return np.sqrt(dx * dx + dy * dy + dz * dz)

    def _is_point_in_collision(
        self, point: Vector3, obstacles: List[ObstacleBox]
    ) -> bool:
        """Проверяет, находится ли точка в коллизии с препятствиями."""
        for obstacle in obstacles:
            if (
                obstacle.min_point.x - SMOOTHER.SAFETY_MARGIN
                <= point.x
                <= obstacle.max_point.x + SMOOTHER.SAFETY_MARGIN
                and obstacle.min_point.y - SMOOTHER.SAFETY_MARGIN
                <= point.y
                <= obstacle.max_point.y + SMOOTHER.SAFETY_MARGIN
                and obstacle.min_point.z - SMOOTHER.SAFETY_MARGIN
                <= point.z
                <= obstacle.max_point.z + SMOOTHER.SAFETY_MARGIN
            ):
                return True
        return False

    def _find_nearest_safe_point(
        self,
        unsafe_point: Vector3,
        obstacles: List[ObstacleBox],
        reference_point: Vector3,
    ) -> Vector3:
        """Находит ближайшую безопасную точку."""
        # Простая реализация: возвращаем reference_point
        # если он безопасен
        if not self._is_point_in_collision(reference_point, obstacles):
            return reference_point
        else:
            # В противном случае возвращаем исходную точку
            return unsafe_point

    def _compute_heading(self, start: Vector3, end: Vector3) -> Rotation:
        """Вычисляет ориентацию на основе направления движения."""
        direction = np.array(
            [end.x - start.x, end.y - start.y, end.z - start.z]
        )

        if np.linalg.norm(direction) < 1e-6:
            return Rotation([0, 0, 0])

        # Нормализуем направление
        direction = direction / np.linalg.norm(direction)

        # Вычисляем углы Эйлера из направления
        yaw = np.arctan2(direction[1], direction[0])
        pitch = np.arcsin(direction[2])
        roll = 0.0  # Предполагаем нулевой крен

        return Rotation([roll, pitch, yaw])

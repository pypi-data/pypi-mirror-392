from typing import List

import numpy as np

from ara_api._utils import (
    BasePlanner,
    ObstacleMap,
    Path,
    PathSegment,
    Rotation,
    Vector3,
)
from ara_api._utils.config import CARROT_PLANNER


class CarrotPlanner(BasePlanner):
    def __init__(self):
        pass

    def plan(
        self, start: Vector3, goal: Vector3, obstacle_map: ObstacleMap
    ) -> Path:
        path = Path()

        if obstacle_map.is_path_clear(
            start, goal, CARROT_PLANNER.SAFETY_MARGIN
        ):
            segment = self.__carrot_create_segment(start, goal, 0)
            path.add_segment(segment)
            return path

        current_point = start
        segment_index = 0

        for iteration in range(CARROT_PLANNER.MAX_ITTERATIONS):
            if (
                self.__distance_2d(current_point, goal)
                < CARROT_PLANNER.MAX_SEGMENT_LENGTH
            ):
                final_segments = (
                    self.__carrot_plan_segment_with_obstacle_avoidance(
                        current_point, goal, segment_index, obstacle_map
                    )
                )
                for segment in final_segments:
                    path.add_segment(segment)
                return path

            distance_to_goal = self.__distance_3d(current_point, goal)

            if distance_to_goal > CARROT_PLANNER.MAX_SEGMENT_LENGTH:
                next_point = Vector3(
                    current_point.x
                    + ((goal.x - current_point.x) / distance_to_goal)
                    * CARROT_PLANNER.MAX_SEGMENT_LENGTH,
                    current_point.y
                    + ((goal.y - current_point.y) / distance_to_goal)
                    * CARROT_PLANNER.MAX_SEGMENT_LENGTH,
                    current_point.z
                    + ((goal.z - current_point.z) / distance_to_goal)
                    * CARROT_PLANNER.MAX_SEGMENT_LENGTH,
                )

                planned_segments = (
                    self.__carrot_plan_segment_with_obstacle_avoidance(
                        current_point, next_point, segment_index, obstacle_map
                    )
                )

                if not planned_segments:
                    print(
                        f"Carrot Planner: "
                        f"Не удалось найти обход на итерации {iteration}"
                    )
                    break

                for segment in planned_segments:
                    path.add_segment(segment)
                    segment_index += 1
                    current_point = segment.end
            else:
                final_segments = (
                    self.__carrot_plan_segment_with_obstacle_avoidance(
                        current_point, goal, segment_index, obstacle_map
                    )
                )
                for segment in final_segments:
                    path.add_segment(segment)
                break

        if (
            path.segments
            and len(path.segments) > 0
            and self.__distance_2d(path.segments[-1].end, goal)
            > CARROT_PLANNER.MAX_SEGMENT_LENGTH * 0.5
        ):
            print("Carrot Planner: Добавляем аварийный сегмент к цели")
            current_end = path.segments[-1].end
            emergency_segment = self.__carrot_create_segment(
                current_end, goal, segment_index
            )
            path.add_segment(emergency_segment)

        if not path.segments:
            print(
                "Carrot Planner: Не удалось построить путь."
                "Добавляем прямой аварийный сегмент."
            )
            emergency_segment = self.__carrot_create_segment(start, goal, 0)
            path.add_segment(emergency_segment)

        return path

    def __distance_2d(self, p1: Vector3, p2: Vector3) -> float:
        """
        Calculate the 2D distance between two points.
        """
        return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def __distance_3d(self, p1: Vector3, p2: Vector3) -> float:
        """
        Calculate the 3D distance between two points.
        """
        return np.sqrt(
            (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2
        )

    def __carrot_plan_segment_with_obstacle_avoidance(
        self,
        segment_start: Vector3,
        segment_end: Vector3,
        segment_index: int,
        obstacle_map: ObstacleMap,
    ) -> List[PathSegment]:
        segments = []

        if obstacle_map.is_path_clear(
            segment_start, segment_end, CARROT_PLANNER.SAFETY_MARGIN
        ):
            segments.append(
                self.__carrot_create_segment(
                    segment_start, segment_end, segment_index
                )
            )
            return segments

        intermediate_height = (
            max(segment_start.z, segment_end.z)
            + CARROT_PLANNER.VERTICAL_CLEARANCE
        )
        intermediate_high = Vector3(
            segment_start.x + (segment_end.x - segment_start.x) * 0.5,
            segment_start.y + (segment_end.y - segment_start.y) * 0.5,
            intermediate_height,
        )

        if obstacle_map.is_path_clear(
            segment_start, intermediate_high, CARROT_PLANNER.SAFETY_MARGIN
        ) and obstacle_map.is_path_clear(
            intermediate_high, segment_end, CARROT_PLANNER.SAFETY_MARGIN
        ):
            segments.append(
                self.__carrot_create_segment(
                    segment_start, intermediate_high, segment_index
                )
            )
            segments.append(
                self.__carrot_create_segment(
                    intermediate_high, segment_end, segment_index + 1
                )
            )
            return segments

        direction_vec = Vector3(
            segment_end.x - segment_start.x,
            segment_end.y - segment_start.y,
            0,
        )
        distance = self.__distance_2d(segment_start, segment_end)

        if distance > 0.001:
            direction_vec.x /= distance
            direction_vec.y /= distance

            perpendicular_left = Vector3(-direction_vec.y, direction_vec.x, 0)
            perpendicular_right = Vector3(direction_vec.y, -direction_vec.x, 0)

            mid_point = Vector3(
                segment_start.x + (segment_end.x - segment_start.x) * 0.5,
                segment_start.y + (segment_end.y - segment_start.y) * 0.5,
                (segment_start.z + segment_end.z) * 0.5,
            )

            left_point = Vector3(
                mid_point.x
                + perpendicular_left.x * CARROT_PLANNER.HORIZONTAL_CLEARANCE,
                mid_point.y
                + perpendicular_left.y * CARROT_PLANNER.HORIZONTAL_CLEARANCE,
                mid_point.z,
            )

            if obstacle_map.is_path_clear(
                segment_start, left_point, CARROT_PLANNER.SAFETY_MARGIN
            ) and obstacle_map.is_path_clear(
                left_point, segment_end, CARROT_PLANNER.SAFETY_MARGIN
            ):
                segments.append(
                    self.__carrot_create_segment(
                        segment_start, left_point, segment_index
                    )
                )
                segments.append(
                    self.__carrot_create_segment(
                        left_point, segment_end, segment_index + 1
                    )
                )
                return segments

            right_point = Vector3(
                mid_point.x
                + perpendicular_right.x * CARROT_PLANNER.HORIZONTAL_CLEARANCE,
                mid_point.y
                + perpendicular_right.y * CARROT_PLANNER.HORIZONTAL_CLEARANCE,
                mid_point.z,
            )

            if obstacle_map.is_path_clear(
                segment_start, right_point, CARROT_PLANNER.SAFETY_MARGIN
            ) and obstacle_map.is_path_clear(
                right_point, segment_end, CARROT_PLANNER.SAFETY_MARGIN
            ):
                segments.append(
                    self.__carrot_create_segment(
                        segment_start, right_point, segment_index
                    )
                )
                segments.append(
                    self.__carrot_create_segment(
                        right_point, segment_end, segment_index + 1
                    )
                )
                return segments

        for clearance_multiplier in [1.0, 1.5, 2.0]:
            high_escape_point = Vector3(
                segment_start.x,
                segment_start.y,
                segment_start.z
                + CARROT_PLANNER.VERTICAL_CLEARANCE * clearance_multiplier,
            )

            high_end_point = Vector3(
                segment_end.x,
                segment_end.y,
                segment_end.z
                + CARROT_PLANNER.VERTICAL_CLEARANCE * clearance_multiplier,
            )

            if (
                obstacle_map.is_path_clear(
                    segment_start,
                    high_escape_point,
                    CARROT_PLANNER.SAFETY_MARGIN,
                )
                and obstacle_map.is_path_clear(
                    high_escape_point,
                    high_end_point,
                    CARROT_PLANNER.SAFETY_MARGIN,
                )
                and obstacle_map.is_path_clear(
                    high_end_point, segment_end, CARROT_PLANNER.SAFETY_MARGIN
                )
            ):
                segments.append(
                    self.__carrot_create_segment(
                        segment_start, high_escape_point, segment_index
                    )
                )
                segments.append(
                    self.__carrot_create_segment(
                        high_escape_point, high_end_point, segment_index + 1
                    )
                )
                segments.append(
                    self.__carrot_create_segment(
                        high_end_point, segment_end, segment_index + 2
                    )
                )
                return segments

        escape_point = Vector3(
            segment_start.x,
            segment_start.y,
            segment_start.z + CARROT_PLANNER.VERTICAL_CLEARANCE,
        )

        if obstacle_map.is_path_clear(
            segment_start, escape_point, CARROT_PLANNER.SAFETY_MARGIN
        ):
            segments.append(
                self.__carrot_create_segment(
                    segment_start, escape_point, segment_index
                )
            )
        else:
            pass

        return segments

    def __carrot_create_segment(
        self, start: Vector3, end: Vector3, segment_index: int
    ) -> PathSegment:
        """
        Create a path segment from start
        to end with the given segment index.
        """
        start_rotation = Rotation.from_two_position(
            start.as_numpy, end.as_numpy
        )
        end_rotation = Rotation.from_two_position(start.as_numpy, end.as_numpy)

        return PathSegment(
            start=start,
            end=end,
            start_heading=start_rotation,
            end_heading=end_rotation,
            metadata={
                "index": segment_index,
                "planner": "carrot",
                "segment_type": "carrot_path",
            },
        )

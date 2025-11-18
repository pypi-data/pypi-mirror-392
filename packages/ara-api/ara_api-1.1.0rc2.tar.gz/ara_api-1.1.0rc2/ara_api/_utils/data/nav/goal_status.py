"""Goal status data class"""

from dataclasses import dataclass


@dataclass
class GoalStatus:
    is_reached: bool = False
    distance_xy: float = float("inf")
    distance_z: float = float("inf")
    yaw_diff: float = float("inf")
    position_reached: bool = False
    yaw_reached: bool = False

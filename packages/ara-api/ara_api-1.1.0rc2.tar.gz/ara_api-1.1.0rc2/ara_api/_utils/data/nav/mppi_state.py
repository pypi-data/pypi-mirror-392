"""MPPI State data class"""

from dataclasses import dataclass, field

from ara_api._utils.data.nav.vector3 import Vector3


@dataclass
class MPPIState:
    """Состояние дрона для MPPI."""

    position: Vector3 = field(default_factory=lambda: Vector3(0.0, 0.0, 0.0))
    velocity: Vector3 = field(default_factory=lambda: Vector3(0.0, 0.0, 0.0))
    yaw: float = 0.0
    yaw_rate: float = 0.0
    timestamp: float = 0.0

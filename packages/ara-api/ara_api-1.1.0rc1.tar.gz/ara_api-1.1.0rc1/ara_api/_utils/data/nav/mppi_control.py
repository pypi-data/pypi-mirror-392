"""MPPI Control data class"""

from dataclasses import dataclass, field

from ara_api._utils.data.nav.vector3 import Vector3


@dataclass
class MPPIControl:
    """Команда управления MPPI."""

    linear_velocity: Vector3 = field(
        default_factory=lambda: Vector3(0.0, 0.0, 0.0)
    )
    angular_velocity: float = 0.0
    timestamp: float = 0.0

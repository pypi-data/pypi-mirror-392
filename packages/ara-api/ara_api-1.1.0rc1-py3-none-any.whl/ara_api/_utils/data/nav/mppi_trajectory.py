"""MPPI Trajectory data class"""

from dataclasses import dataclass, field
from typing import List

from ara_api._utils.data.nav.mppi_control import MPPIControl
from ara_api._utils.data.nav.mppi_state import MPPIState


@dataclass
class MPPITrajectory:
    """Сэмплированная траектория MPPI."""

    states: List[MPPIState] = field(default_factory=list)
    controls: List[MPPIControl] = field(default_factory=list)
    cost: float = 0.0
    weight: float = 0.0

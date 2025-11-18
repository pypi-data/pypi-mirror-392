import math
from typing import Optional

import numpy as np

from ara_api._utils import MPPIControl, MPPIState, Vector3
from ara_api._utils.config import MPPI


class MPPIDynamicsModel:
    """
    Модель динамики дрона для MPPI.

    Реализует простую кинематическую модель дрона с учетом ограничений
    на скорости и ускорения.
    """

    def __init__(self):
        """Инициализация модели динамики."""
        self._dt = 1.0 / MPPI.CONTROL_FREQUENCY

        self._vel_alpha = math.exp(-self._dt / MPPI.VELOCITY_TAU)
        self._yaw_alpha = math.exp(-self._dt / MPPI.ANGULAR_TAU)

    def predict_next_state_batch(
        self, states: np.ndarray, controls: np.ndarray
    ) -> np.ndarray:
        pos = states[:, :3]
        vel = states[:, 3:6]
        yaw = states[:, 6]
        yaw_rate = states[:, 7]

        control_vel = controls[:, :3]
        control_yaw_rate = controls[:, 3]

        new_vel = vel * self._vel_alpha + control_vel * (1 - self._vel_alpha)
        new_yaw_rate = yaw_rate * self._yaw_alpha + control_yaw_rate * (
            1 - self._yaw_alpha
        )

        new_pos = pos + new_vel * self._dt
        new_yaw = yaw + new_yaw_rate * self._dt

        new_yaw = (new_yaw + np.pi) % (2 * np.pi) - np.pi

        next_states = np.column_stack(
            [new_pos, new_vel, new_yaw, new_yaw_rate]
        )
        return next_states

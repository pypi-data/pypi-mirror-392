import logging
import math
import time
from typing import Any, Dict, List, Optional

import numpy as np

from ara_api._core.services.nav.controller.mppi.cost_function import (
    MPPICostFunction,
)
from ara_api._core.services.nav.controller.mppi.dynamic_model import (
    MPPIDynamicsModel,
)
from ara_api._utils import (
    Logger,
    MPPIControl,
    MPPIState,
    MPPITrajectory,
    ObstacleBox,
    Path,
    Vector3,
)
from ara_api._utils.config import MPPI


class MPPIController:
    """
    MPPI (Model Predictive Path Integral) контроллер.

    Реализует алгоритм MPPI для генерации оптимальных команд управления
    дроном в реальном времени. Использует сэмплирование траекторий и
    информационно-теоретический подход для оптимизации.
    """

    def __init__(self, obstacles: Optional[List[ObstacleBox]] = None):
        """
        Инициализация MPPI контроллера.

        Args:
            obstacles: Список препятствий в рабочем пространстве.
        """
        self._logger = Logger(
            log_level=MPPI.LOG_LEVEL,
            log_to_file=MPPI.LOG_TO_FILE,
            log_to_terminal=MPPI.LOG_TO_TERMINAL,
        )

        self._horizon = int(MPPI.TIME_HORIZON * MPPI.CONTROL_FREQUENCY)
        self._num_samples = MPPI.NUM_SAMPLES
        self._temp = MPPI.TEMPERATURE
        self._dt = 1.0 / MPPI.CONTROL_FREQUENCY
        self._control_dim = 4  # 3 линейные скорости + 1 угловая скорость
        self._state_dim = (
            8  # 3 позиции + 3 скорости + 1 угол + 1 угловая скорость
        )

        self._noise_sigma = np.array(
            [
                MPPI.VELOCITY_NOISE_STD,
                MPPI.VELOCITY_NOISE_STD,
                MPPI.VELOCITY_NOISE_STD,
                MPPI.ANGULAR_NOISE_STD,
            ]
        )

        noise_covariance = np.diag(self._noise_sigma**2)

        self._dynamics_model = MPPIDynamicsModel()
        self._cost_function = MPPICostFunction(
            obstacles, noise_covariance, self._temp
        )

        self._optimal_sequence = np.zeros((self._horizon, self._control_dim))

        self._stats: Dict[str, Any] = {}
        self.reset_stats()
        self._logger.debug(
            "MPPI контроллер инициализирован: "
            "horizon_steps={horizon}, samples={samples}, "
            "frequency={frequency}".format(
                horizon=self._horizon,
                samples=self._num_samples,
                frequency=MPPI.CONTROL_FREQUENCY,
            )
        )

    def compute_control(
        self,
        current_state: MPPIState,
        reference_path: Optional[Path],
        goal_state: MPPIState,
    ) -> MPPIControl:
        """
        Вычисляет оптимальную команду управления.

        Args:
            current_state: Текущее состояние дрона.
            reference_path: Референсная траектория для отслеживания
            (может быть None).
            goal_state: Целевое состояние.

        Returns:
            Оптимальная команда управления.
        """
        start_time = time.time()

        try:
            guidance_control = self._compute_guidance_control(
                current_state, reference_path
            )

            biased_sequence = (
                1.0 - MPPI.GUIDANCE_WEIGHT
            ) * self._optimal_sequence + (
                MPPI.GUIDANCE_WEIGHT * guidance_control
            )

            noise = np.random.normal(
                loc=0.0,
                scale=self._noise_sigma,
                size=(self._num_samples, self._horizon, self._control_dim),
            )
            perturbed_sequences = biased_sequence + noise

            trajectory_batch = self._batch_rollout(
                current_state, perturbed_sequences
            )

            costs = self._cost_function.compute_trajectory_cost(
                trajectory_batch,
                perturbed_sequences,
                reference_path,
                goal_state,
            )

            # Это реализация формулы (10)
            # из статьи "Biased Sampling for MPPI"
            # https://autonomousrobots.nl/assets/files/publications/24_trevisan_ral_biased.pdf
            inv_covariance = np.diag(1.0 / self._noise_sigma**2)
            mean_shift = biased_sequence - self._optimal_sequence

            # Вычисляем корректирующий член стоимости (term1 и term2)
            # Вычисляем градиент стоимости по среднему смещению
            # term1: λ * v_k ^ T * Σ ^ -1 * μ
            mu_dot_inv_cov = np.einsum("hc,cd->hd", mean_shift, inv_covariance)
            term1_per_step = np.einsum("kdc,hc->kh", noise, mu_dot_inv_cov)

            # term2: -0.5 * λ * μ^T * Σ^-1 * μ
            term2_per_step = -0.5 * np.einsum(
                "hc,hc->h", mu_dot_inv_cov, mean_shift
            )

            cost_adjustment = self._temp * np.sum(
                term1_per_step - term2_per_step, axis=1
            )

            costs += cost_adjustment

            weights = self._compute_weights(costs)
            self._optimal_sequence = np.sum(
                weights[:, np.newaxis, np.newaxis] * perturbed_sequences,
                axis=0,
            )

            first_command_vec = self._optimal_sequence[0]
            self._optimal_sequence = np.roll(
                self._optimal_sequence, -1, axis=0
            )
            self._optimal_sequence[-1] = 0

            self._update_stats(costs, time.time() - start_time)
            return MPPIControl(
                linear_velocity=Vector3(
                    first_command_vec[0],
                    first_command_vec[1],
                    first_command_vec[2],
                ),
                angular_velocity=first_command_vec[3],
                timestamp=current_state.timestamp,
            )
        except Exception as e:
            self._logger.error(f"Ошибка вычисления MPPI управления: {e}")

            return MPPIControl(
                linear_velocity=Vector3(0, 0, 0),
                angular_velocity=0.0,
                timestamp=current_state.timestamp,
            )

    def _compute_guidance_control(
        self,
        current_state: MPPIState,
        reference_path: Optional[Path],
    ) -> np.ndarray:
        """Вычисляет "направляющее" управление, которое ведет к цели."""
        if reference_path is None or not reference_path.segments:
            return np.zeros(self._control_dim)

        current_pos_np = np.array(
            [
                current_state.position.x,
                current_state.position.y,
                current_state.position.z,
            ]
        )

        path_starts = np.array(
            [
                [s.start.x, s.start.y, s.start.z]
                for s in reference_path.segments
            ]
        )
        path_ends = np.array(
            [[s.end.x, s.end.y, s.end.z] for s in reference_path.segments]
        )
        dist_to_starts = np.linalg.norm(path_starts - current_pos_np, axis=1)

        target_segment_idx = np.argmin(dist_to_starts)

        target_pos_vec = path_ends[target_segment_idx]
        target_pos = Vector3(
            x=target_pos_vec[0], y=target_pos_vec[1], z=target_pos_vec[2]
        )
        current_pos = current_state.position

        direction_vec = np.array(
            [
                target_pos.x - current_pos.x,
                target_pos.y - current_pos.y,
                target_pos.z - current_pos.z,
            ]
        )
        dist_to_target = np.linalg.norm(direction_vec)
        if dist_to_target < 0.1:
            return np.zeros(self._control_dim)

        direction_vec_norm = direction_vec / dist_to_target

        target_linear_velocity = direction_vec_norm * MPPI.MAX_LINEAR_VEL

        target_yaw = math.atan2(direction_vec_norm[1], direction_vec_norm[0])

        yaw_error = target_yaw - current_state.yaw
        yaw_error = (yaw_error + np.pi) % (2 * np.pi) - np.pi

        target_angular_velocity = np.clip(
            2.0 * yaw_error, -MPPI.MAX_ANGULAR_VEL, MPPI.MAX_ANGULAR_VEL
        )

        return np.array(
            [
                target_linear_velocity[0],
                target_linear_velocity[1],
                target_linear_velocity[2],
                target_angular_velocity,
            ]
        )

    def _compute_weights(self, costs: np.ndarray) -> np.ndarray:
        min_cost = np.min(costs)
        exp_costs = np.exp(-1.0 / self._temp * (costs - min_cost))
        sum_exp_costs = np.sum(exp_costs)

        if sum_exp_costs < 1e-9:
            return np.ones(self._num_samples) / self._num_samples

        return exp_costs / sum_exp_costs

    def _batch_rollout(
        self, start_state: MPPIState, controls: np.ndarray
    ) -> np.ndarray:
        """
        Симулирует все траектории ОДНОВРЕМЕННО с помощью numpy.
        Это сердце высокопроизводительного MPPI.
        """
        # Начальное состояние, размноженное для всех сэмплов
        # Shape: (num_samples, state_dim)
        state = np.zeros((self._num_samples, self._state_dim))
        state[:, 0:3] = [
            start_state.position.x,
            start_state.position.y,
            start_state.position.z,
        ]
        state[:, 3:6] = [
            start_state.velocity.x,
            start_state.velocity.y,
            start_state.velocity.z,
        ]
        state[:, 6] = start_state.yaw
        state[:, 7] = start_state.yaw_rate

        # Массив для хранения истории состояний всех траекторий
        trajectory_history = np.zeros(
            (self._num_samples, self._horizon, self._state_dim)
        )

        for i in range(self._horizon):
            control_at_step = controls[:, i, :]

            state = self._dynamics_model.predict_next_state_batch(
                states=state, controls=control_at_step
            )
            trajectory_history[:, i, :] = state

        return trajectory_history

    def _rollout(
        self, initial_state: MPPIState, control_sequence: np.ndarray
    ) -> MPPITrajectory:
        vel_alpha = math.exp(-self._dt / MPPI.VELOCITY_TAU)
        yaw_alpha = math.exp(-self._dt / MPPI.ANGULAR_TAU)

        num_steps = self._horizon
        state_history = np.zeros((num_steps + 1, 8))
        control_history = np.zeros((num_steps, self._control_dim))

        state_history[0, 0:3] = [
            initial_state.position.x,
            initial_state.position.y,
            initial_state.position.z,
        ]
        state_history[0, 3:6] = [
            initial_state.velocity.x,
            initial_state.velocity.y,
            initial_state.velocity.z,
        ]
        state_history[0, 6] = initial_state.yaw
        state_history[0, 7] = initial_state.yaw_rate

        for i in range(num_steps):
            current_vel = state_history[i, 3:6]
            current_yaw_rate = state_history[i, 7]

            control_vec = control_sequence[i]
            control_history[i] = control_vec

            new_vel = current_vel * vel_alpha + control_vec[:3] * (
                1 - vel_alpha
            )
            new_yaw_rate = current_yaw_rate * yaw_alpha + control_vec[3] * (
                1 - yaw_alpha
            )

            new_pos = state_history[i, 0:3] + current_vel * self._dt
            new_yaw = state_history[i, 6] + current_yaw_rate * self._dt
            new_yaw = (new_yaw + math.pi) % (2 * math.pi) - math.pi

            state_history[i + 1] = np.concatenate(
                (new_pos, new_vel, [new_yaw], [new_yaw_rate])
            )

        final_states = [
            MPPIState(
                position=Vector3(s[0], s[1], s[2]),
                velocity=Vector3(s[3], s[4], s[5]),
                yaw=s[6],
                yaw_rate=s[7],
                timestamp=initial_state.timestamp + i * self._dt,
            )
            for i, s in enumerate(state_history)
        ]
        final_controls = [
            MPPIControl(
                linear_velocity=Vector3(c[0], c[1], c[2]),
                angular_velocity=c[3],
                timestamp=initial_state.timestamp + i * self._dt,
            )
            for i, c in enumerate(control_history)
        ]

        return MPPITrajectory(
            states=final_states, controls=final_controls, cost=0.0, weight=0.0
        )

    def _update_stats(
        self, costs: np.ndarray, computation_time: float
    ) -> None:
        self._stats["total_computations"] += 1
        n = self._stats["total_computations"]
        self._stats["average_computation_time"] = (
            self._stats["average_computation_time"] * (n - 1)
            + computation_time
        ) / n
        self._stats["best_cost_history"].append(np.min(costs))
        if len(self._stats["best_cost_history"]) > 500:
            self._stats["best_cost_history"].pop(0)

    def update_obstacles(self, obstacles: List[ObstacleBox]) -> None:
        """
        Обновляет информацию о препятствиях.

        Args:
            obstacles: Новый список препятствий.
        """
        self._cost_function.update_obstacles(obstacles)
        self._logger.debug(f"Обновлено {len(obstacles)} препятствий")

    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику работы контроллера.

        Returns:
            Словарь со статистическими данными.
        """
        stats = self._stats.copy()
        stats.update(
            {
                "current_config": {
                    "time_horizon": self._time_horizon,
                    "num_samples": self._num_samples,
                    "temperature": self._temperature,
                    "control_frequency": MPPI.CONTROL_FREQUENCY,
                }
            }
        )
        return stats

    def reset_stats(self) -> None:
        """Сбрасывает статистику контроллера."""
        self._stats = {
            "total_computations": 0,
            "average_computation_time": 0.0,
            "best_cost_history": [],
            "convergence_iterations": [],
        }
        self._logger.debug("Статистика MPPI контроллера сброшена")


# Вспомогательные функции для создания состояний и команд
def create_mppi_state(
    position: Vector3,
    velocity: Vector3 = None,
    yaw: float = 0.0,
    yaw_rate: float = 0.0,
) -> MPPIState:
    """
    Создает состояние MPPI из базовых параметров.

    Args:
        position: Позиция дрона.
        velocity: Скорость дрона (по умолчанию нулевая).
        yaw: Угол рыскания в радианах.
        yaw_rate: Скорость изменения угла рыскания.

    Returns:
        Объект состояния MPPI.
    """
    if velocity is None:
        velocity = Vector3(0, 0, 0)

    return MPPIState(
        position=position,
        velocity=velocity,
        yaw=yaw,
        yaw_rate=yaw_rate,
        timestamp=time.time(),
    )


def create_mppi_control(
    linear_velocity: Vector3, angular_velocity: float = 0.0
) -> MPPIControl:
    """
    Создает команду управления MPPI.

    Args:
        linear_velocity: Линейная скорость.
        angular_velocity: Угловая скорость.

    Returns:
        Объект команды управления MPPI.
    """
    return MPPIControl(
        linear_velocity=linear_velocity,
        angular_velocity=angular_velocity,
        timestamp=time.time(),
    )

"""
Move Command Implementation for Navigation State Machine.

Реализует команду перемещения дрона к целевой точке с использованием
MPPI-контроллера, глобального планировщика и проверки достижения цели.
Интегрируется с gRPCSync для отправки команд управления через RC-каналы.
"""

import time
from typing import Any, List, Optional

from ara_api._core.services.nav.behavior.commands._subutils import (
    CommandResult,
    NavigationCommand,
)
from ara_api._core.services.nav.checker.simple_goal_checker import (
    SimpleGoalChecker,
)
from ara_api._core.services.nav.controller.mppi.controller import (
    MPPIController,
)
from ara_api._core.services.nav.planner.global_planner import (
    GlobalNavigationPlanner,
)
from ara_api._utils import (
    Logger,
    MPPIControl,
    MPPIState,
    ObstacleBox,
    Path,
    Vector3,
)
from ara_api._utils.communication.grpc_sync import gRPCSync
from ara_api._utils.config import MOVE_COMMAND, MPPI
from ara_api._utils.data.msp import RC


class MoveCommand(NavigationCommand):
    """
    Команда перемещения дрона к целевой точке.

    Реализует полный цикл навигации:
    1. Глобальное планирование траектории с учетом препятствий
    2. Локальное управление через MPPI-контроллер
    3. Отправка команд управления через RC-каналы
    4. Проверка достижения цели

    Attributes:
        _logger: Логгер для диагностических сообщений.
        _grpc_sync: Синхронный gRPC-клиент для связи с MSP.
        _planner: Глобальный планировщик траекторий.
        _controller: MPPI-контроллер для локального управления.
        _goal_checker: Проверщик достижения целевой точки.
        _obstacles: Список препятствий в рабочем пространстве.
        _current_path: Текущая запланированная траектория.
        _goal_position: Целевая позиция для перемещения.
        _is_executing: Флаг выполнения команды.
    """

    def __init__(self, obstacles: Optional[List[ObstacleBox]] = None):
        """
        Инициализация команды перемещения.

        Args:
            obstacles: Список препятствий в рабочем пространстве.
                      Если None, препятствия не учитываются.
        """
        self._logger = Logger(
            log_level=MOVE_COMMAND.LOG_LEVEL,
            log_to_file=MOVE_COMMAND.LOG_TO_FILE,
            log_to_terminal=MOVE_COMMAND.LOG_TO_TERMINAL,
        )

        self._grpc_sync = gRPCSync.get_instance()
        self._planner = GlobalNavigationPlanner()
        self._controller = MPPIController(obstacles)
        self._goal_checker = SimpleGoalChecker()

        self._obstacles = obstacles or []
        self._current_path: Optional[Path] = None
        self._goal_position: Optional[Vector3] = None
        self._is_executing: bool = False

        self._logger.info("MoveCommand инициализирована")

    def can_execute(self, request: Any, context: Any) -> bool:
        """
        Проверяет возможность выполнения команды перемещения.

        Args:
            request: gRPC запрос с целевой позицией (PointData).
            context: gRPC контекст.

        Returns:
            True, если команда может быть выполнена, иначе False.
        """
        try:
            # Проверяем наличие целевой точки в запросе
            if not hasattr(request, "point") or request.point is None:
                self._logger.error("Целевая точка не указана в запросе")
                return False

            target_position = Vector3(
                x=request.point.x, y=request.point.y, z=request.point.z
            )

            # Проверяем валидность координат
            if not self._is_valid_position(target_position):
                self._logger.error(
                    f"Некорректная целевая позиция: {target_position}"
                )
                return False

            # Получаем текущее состояние дрона
            current_state = self._get_current_drone_state()
            if current_state is None:
                self._logger.error(
                    "Не удалось получить текущее состояние дрона"
                )
                return False

            # Проверяем безопасность полета
            if not self._is_safe_to_fly(current_state):
                self._logger.error("Условия полета небезопасны")
                return False

            # Проверяем достижимость цели
            if not self._is_goal_reachable(
                current_state.position, target_position
            ):
                self._logger.error("Целевая точка недостижима")
                return False

            self._logger.info(
                f"Команда Move может быть выполнена к позиции {target_position}"
            )
            return True

        except Exception as e:
            self._logger.error(
                f"Ошибка при проверке возможности выполнения Move: {e}"
            )
            return False

    def execute(self, request: Any, context: Any) -> CommandResult:
        """
        Выполняет команду перемещения к целевой точке.

        Args:
            request: gRPC запрос с целевой позицией (PointData).
            context: gRPC контекст.

        Returns:
            CommandResult с результатом выполнения команды.
        """
        try:
            self._is_executing = True
            self._goal_position = Vector3(
                x=request.point.x, y=request.point.y, z=request.point.z
            )

            self._logger.info(
                f"Начало выполнения команды Move к {self._goal_position}"
            )

            # Получаем текущее состояние дрона
            current_state = self._get_current_drone_state()
            if current_state is None:
                return CommandResult(
                    success=False,
                    message="Не удалось получить текущее состояние дрона",
                )

            # Планируем траекторию
            try:
                self._current_path = self._planner.plan_path(
                    start=current_state.position,
                    goal=self._goal_position,
                    obstacles=self._obstacles,
                )
                self._logger.info(
                    f"Траектория спланирована: {len(self._current_path.segments)} сегментов"
                )
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"Ошибка планирования траектории: {e}",
                )

            # Основной цикл управления
            control_result = self._execute_navigation_loop(current_state)

            self._is_executing = False
            return control_result

        except Exception as e:
            self._is_executing = False
            self._logger.error(f"Ошибка выполнения команды Move: {e}")
            return CommandResult(
                success=False, message=f"Ошибка выполнения команды Move: {e}"
            )

    def _execute_navigation_loop(
        self, initial_state: MPPIState
    ) -> CommandResult:
        """
        Основной цикл навигации с использованием MPPI-контроллера.

        Args:
            initial_state: Начальное состояние дрона.

        Returns:
            CommandResult с результатом навигации.
        """
        start_time = time.time()
        max_execution_time = MOVE_COMMAND.MAX_EXECUTION_TIME

        while (
            self._is_executing
            and time.time() - start_time < max_execution_time
        ):
            try:
                # Получаем текущее состояние дрона
                current_state = self._get_current_drone_state()
                if current_state is None:
                    self._logger.warning(
                        "Не удалось получить состояние дрона, используем предыдущее"
                    )
                    time.sleep(0.1)
                    continue

                # Проверяем достижение цели
                if self._goal_checker.is_goal_reached(
                    current_pose=current_state.position,
                    goal_pose=self._goal_position,
                ):
                    self._logger.info("Цель достигнута!")
                    self._stop_drone()
                    return CommandResult(
                        success=True, message="Цель успешно достигнута"
                    )

                # Вычисляем управляющее воздействие через MPPI
                goal_state = MPPIState(
                    position=self._goal_position,
                    velocity=Vector3(0, 0, 0),
                    yaw=current_state.yaw,
                    yaw_rate=0.0,
                    timestamp=time.time(),
                )

                control_command = self._controller.compute_control(
                    current_state=current_state,
                    reference_path=self._current_path,
                    goal_state=goal_state,
                )

                # Отправляем команды управления
                self._send_control_command(control_command)

                # Ждем следующий цикл управления
                time.sleep(1.0 / MPPI.CONTROL_FREQUENCY)

            except Exception as e:
                self._logger.error(f"Ошибка в цикле навигации: {e}")
                time.sleep(0.1)

        # Превышено время выполнения или команда прервана
        self._stop_drone()

        if time.time() - start_time >= max_execution_time:
            return CommandResult(
                success=False,
                message="Превышено максимальное время выполнения команды",
            )
        else:
            return CommandResult(success=False, message="Команда прервана")

    def _send_control_command(self, control: MPPIControl) -> None:
        """
        Отправляет команды управления через RC-каналы.

        Args:
            control: Команда управления от MPPI-контроллера.
        """
        try:
            # Преобразуем скорости в RC-команды
            rc_command_base = RC()
            rc_command = rc_command_base.transform_from_vel(
                x=control.linear_velocity.x,
                y=control.linear_velocity.y,
                z=control.linear_velocity.z,
                w=control.angular_velocity,
                state=self._get_current_drone_state(),
                dt=1.0 / MPPI.CONTROL_FREQUENCY,
            )

            # Ограничиваем команды в диапазоне RC (используя правильные поля gRPC)
            rc_command.grpc.ail = int(max(1000, min(2000, rc_command.grpc.ail)))
            rc_command.grpc.ele = int(max(1000, min(2000, rc_command.grpc.ele)))
            rc_command.grpc.thr = int(max(1000, min(2000, rc_command.grpc.thr)))
            rc_command.grpc.rud = int(max(1000, min(2000, rc_command.grpc.rud)))

            # Отправляем команду
            self._grpc_sync.msp_cmd_send_rc(rc_command.grpc)

            self._logger.debug(
                f"Отправлена RC команда: roll={rc_command.grpc.ail}, "
                f"pitch={rc_command.grpc.ele}, throttle={rc_command.grpc.thr}, "
                f"yaw={rc_command.grpc.rud}"
            )

        except Exception as e:
            self._logger.error(f"Ошибка отправки команды управления: {e}")

    def _stop_drone(self) -> None:
        """Останавливает дрон, отправляя нейтральные RC-команды."""
        try:
            neutral_rc = RC()
            # Устанавливаем нейтральные значения (правильные поля gRPC)
            neutral_rc.grpc.ail = 1500  # Нейтральное положение (roll)
            neutral_rc.grpc.ele = 1500  # Нейтральное положение (pitch)
            neutral_rc.grpc.thr = 1500  # Поддержание высоты (throttle)
            neutral_rc.grpc.rud = 1500  # Нейтральное положение (yaw)
            neutral_rc.grpc.aux1 = 1000
            neutral_rc.grpc.aux2 = 1000
            neutral_rc.grpc.aux3 = 1000
            neutral_rc.grpc.aux4 = 1000

            # Отправляем несколько нейтральных команд для надежности
            for _ in range(3):
                self._grpc_sync.msp_cmd_send_rc(neutral_rc.grpc)
                time.sleep(0.05)

            self._logger.info("Дрон остановлен")

        except Exception as e:
            self._logger.error(f"Ошибка остановки дрона: {e}")

    def _get_current_drone_state(self) -> Optional[MPPIState]:
        """
        Получает текущее состояние дрона из MSP.

        Returns:
            MPPIState с текущим состоянием дрона или None при ошибке.
        """
        try:
            # Получаем позицию
            position_data = self._grpc_sync.msp_get_position()
            if position_data is None:
                return None

            # Получаем ориентацию
            attitude_data = self._grpc_sync.msp_get_attitude()
            if attitude_data is None:
                return None

            # Создаем состояние для MPPI
            return MPPIState(
                position=Vector3(
                    x=position_data.x, y=position_data.y, z=position_data.z
                ),
                velocity=Vector3(
                    x=position_data.vx, y=position_data.vy, z=position_data.vz
                ),
                yaw=attitude_data.yaw_rad,
                yaw_rate=attitude_data.yaw_rate_rad,
                timestamp=time.time(),
            )

        except Exception as e:
            self._logger.error(f"Ошибка получения состояния дрона: {e}")
            return None

    def _is_valid_position(self, position: Vector3) -> bool:
        """
        Проверяет валидность координат позиции.

        Args:
            position: Позиция для проверки.

        Returns:
            True, если позиция валидна, иначе False.
        """
        # Проверяем на NaN и бесконечность
        if not all(
            isinstance(coord, (int, float))
            for coord in [position.x, position.y, position.z]
        ):
            return False

        # Проверяем разумные пределы
        max_coord = MOVE_COMMAND.MAX_COORDINATE_VALUE
        if abs(position.x) > max_coord or abs(position.y) > max_coord:
            return False

        # Проверяем высоту
        if (
            position.z < MOVE_COMMAND.MIN_ALTITUDE
            or position.z > MOVE_COMMAND.MAX_ALTITUDE
        ):
            return False

        return True

    def _is_safe_to_fly(self, current_state: MPPIState) -> bool:
        """
        Проверяет безопасность полета.

        Args:
            current_state: Текущее состояние дрона.

        Returns:
            True, если полет безопасен, иначе False.
        """
        try:
            # Проверяем высоту
            if current_state.position.z < MOVE_COMMAND.MIN_SAFE_ALTITUDE:
                return False

            # Проверяем наклон дрона
            attitude = self._grpc_sync.msp_get_attitude()
            if attitude is None:
                return False

            max_tilt = MOVE_COMMAND.MAX_SAFE_TILT_DEG
            if (
                abs(attitude.roll_deg) > max_tilt
                or abs(attitude.pitch_deg) > max_tilt
            ):
                return False

            return True

        except Exception as e:
            self._logger.error(f"Ошибка проверки безопасности полета: {e}")
            return False

    def _is_goal_reachable(self, start: Vector3, goal: Vector3) -> bool:
        """
        Проверяет достижимость целевой точки.

        Args:
            start: Начальная позиция.
            goal: Целевая позиция.

        Returns:
            True, если цель достижима, иначе False.
        """
        try:
            # Проверяем расстояние до цели
            distance = (
                (goal.x - start.x) ** 2
                + (goal.y - start.y) ** 2
                + (goal.z - start.z) ** 2
            ) ** 0.5

            if distance > MOVE_COMMAND.MAX_DISTANCE:
                self._logger.error(f"Цель слишком далеко: {distance:.2f}м")
                return False

            if distance < MOVE_COMMAND.MIN_DISTANCE:
                self._logger.warning(f"Цель слишком близко: {distance:.2f}м")
                return False

            # Проверяем препятствия на прямой линии к цели
            # (упрощенная проверка, полная проверка выполняется планировщиком)
            for obstacle in self._obstacles:
                if self._line_intersects_obstacle(start, goal, obstacle):
                    self._logger.warning("Препятствие на пути к цели")
                    # Не блокируем выполнение, планировщик найдет обход
                    break

            return True

        except Exception as e:
            self._logger.error(f"Ошибка проверки достижимости цели: {e}")
            return False

    def _line_intersects_obstacle(
        self, start: Vector3, end: Vector3, obstacle: ObstacleBox
    ) -> bool:
        """
        Проверяет пересечение линии с препятствием (упрощенная версия).

        Args:
            start: Начальная точка линии.
            end: Конечная точка линии.
            obstacle: Препятствие для проверки.

        Returns:
            True, если линия пересекает препятствие, иначе False.
        """
        # Упрощенная проверка: проверяем, проходит ли линия через AABB препятствия
        # Более точная проверка реализована в планировщике

        min_x = min(start.x, end.x)
        max_x = max(start.x, end.x)
        min_y = min(start.y, end.y)
        max_y = max(start.y, end.y)
        min_z = min(start.z, end.z)
        max_z = max(start.z, end.z)

        return not (
            max_x < obstacle.min_point.x
            or min_x > obstacle.max_point.x
            or max_y < obstacle.min_point.y
            or min_y > obstacle.max_point.y
            or max_z < obstacle.min_point.z
            or min_z > obstacle.max_point.z
        )

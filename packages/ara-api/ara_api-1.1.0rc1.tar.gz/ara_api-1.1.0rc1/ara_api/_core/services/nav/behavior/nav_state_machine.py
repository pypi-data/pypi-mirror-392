import threading
from concurrent.futures import Future, ProcessPoolExecutor
from typing import Any, Dict, List, Optional, Set

from ara_api._core.services.nav.behavior.commands._subutils import (
    CommandResult,
    NavigationCommand,
)
from ara_api._utils import (
    DroneState,
    Logger,
    NavigationState,
    NavigationStateCached,
)


class NavigationStateMachine:
    """Управляет навигационными состояниями и командами дрона.

    Этот класс оркестрирует переходы между состояниями навигации и выполняет
    соответствующие команды, используя ProcessPoolExecutor для CPU-интенсивных
    задач.
    """

    def __init__(self, logger: Logger, max_workers: int = 4):
        """Инициализирует машину состояний.

        Args:
            logger: Экземпляр логгера для записи событий.
            max_workers: Максимальное количество рабочих процессов для пула.
        """
        self._current_state = NavigationState.IDLE
        self._logger = logger
        self._lock = threading.Lock()

        # Инициализируем пул процессов один раз при создании экземпляра
        self._process_pool: ProcessPoolExecutor = ProcessPoolExecutor(
            max_workers=max_workers
        )
        self._max_workers = max_workers

        # Текущая выполняющаяся команда
        self._current_command: Optional[Future] = None
        self._current_command_instance: Optional[NavigationCommand] = None

        # Singleton кеш для навигационных данных
        self._nav_cache = NavigationStateCached()

        # Таблица допустимых переходов между состояниями
        self._transitions: Dict[NavigationState, Set[NavigationState]] = {
            NavigationState.IDLE: {
                NavigationState.TAKEOFF,
                NavigationState.EMERGENCY,
            },
            NavigationState.TAKEOFF: {
                NavigationState.FLYING,
                NavigationState.EMERGENCY,
            },
            NavigationState.LAND: {
                NavigationState.IDLE,
                NavigationState.EMERGENCY,
            },
            NavigationState.MOVE: {
                NavigationState.FLYING,
                NavigationState.SPEED,
                NavigationState.ALTITUDE,
                NavigationState.LAND,
                NavigationState.EMERGENCY,
            },
            NavigationState.SPEED: {
                NavigationState.FLYING,
                NavigationState.ALTITUDE,
                NavigationState.MOVE,
                NavigationState.LAND,
                NavigationState.EMERGENCY,
            },
            NavigationState.ALTITUDE: {
                NavigationState.FLYING,
                NavigationState.SPEED,
                NavigationState.MOVE,
                NavigationState.LAND,
                NavigationState.EMERGENCY,
            },
            NavigationState.FLYING: {
                NavigationState.MOVE,
                NavigationState.LAND,
                NavigationState.SPEED,
                NavigationState.ALTITUDE,
                NavigationState.EMERGENCY,
            },
            NavigationState.EMERGENCY: {
                NavigationState.IDLE,
                NavigationState.LAND,
            },
        }

        self._logger.debug(
            f"NavigationStateMachine инициализирована. "
            f"Начальное состояние: {self._current_state.name}"
        )

    def transition(self, new_state: NavigationState, *args, **kwargs) -> None:
        """Осуществляет переход машины состояний в новое состояние.

        При переходе автоматически запускается соответствующая команда.

        Args:
            new_state: Новое состояние для перехода.
            *args: Позиционные аргументы для команды состояния.
            **kwargs: Именованные аргументы для команды состояния.

        Raises:
            ValueError: Если переход из текущего состояния в новое невозможен.
        """
        with self._lock:
            if new_state not in self._transitions[self._current_state]:
                error_msg = (
                    f"Невозможно перейти из состояния {self._current_state.name} "
                    f"в {new_state.name}"
                )
                self._logger.error(error_msg)
                raise ValueError(error_msg)

            # Удаляем state из kwargs если он есть (он больше не нужен)
            kwargs.pop("state", None)

            # Выполняем выход из текущего состояния
            self._execute_exit_method(self._current_state)

            self._logger.info(
                f"Переход из состояния {self._current_state.name} "
                f"в {new_state.name}"
            )

            self._current_state = new_state

            # Выполняем вход в новое состояние и запускаем команду
            self._execute_enter_method(self._current_state, *args, **kwargs)

    def handle_command(
        self, command_instance: NavigationCommand, *args, **kwargs
    ) -> None:
        """Обрабатывает входящую навигационную команду.

        Args:
            command_instance: Экземпляр команды для выполнения.
            *args: Позиционные аргументы для команды.
            **kwargs: Именованные аргументы для команды.

        Raises:
            RuntimeError: Если уже выполняется другая команда.
            ValueError: Если команда не может быть выполнена.
        """
        self._logger.debug(
            f"Обработка команды: {type(command_instance).__name__}"
        )
        if (
            self._current_command is not None
            and not self._current_command.done()
        ):
            raise RuntimeError("Уже выполняется другая команда")

        if not command_instance.can_execute(*args, **kwargs):
            raise ValueError("Команда не может быть выполнена")

        self._logger.info(
            f"Начало выполнения команды: {type(command_instance).__name__}"
        )

        self._current_command_instance = command_instance

        self._logger.debug(
            "Параметры команды {name}(handler): {kw}".format(
                name=type(command_instance).__name__, kw=kwargs
            )
        )

        # Определяем, нужно ли выполнять команду в отдельном процессе
        if self._is_cpu_intensive_command(command_instance):
            self._logger.debug(
                "Команда {} требует выполнения в отдельном процессе".format(
                    type(command_instance).__name__
                )
            )
            future = self._process_pool.submit(
                command_instance.execute, *args, **kwargs
            )
            self._current_command = future
            future.add_done_callback(
                lambda f: self._on_command_complete(f, command_instance)
            )
        else:
            # Выполняем простую команду синхронно
            try:
                self._logger.debug(
                    "Команда {} требует синхронного выполнения".format(
                        type(command_instance).__name__
                    )
                )
                result = command_instance.execute(*args, **kwargs)
                self._on_command_success(result, command_instance)
            except Exception as e:
                import traceback

                self._logger.error(
                    f"Ошибка при выполнении команды {type(command_instance).__name__}: {e}\n"
                    f"{traceback.format_exc()}"
                )
                self._on_command_error(e, command_instance)

    def _on_command_complete(
        self, future: Future, command_instance: NavigationCommand
    ) -> None:
        """Колбэк по завершении выполнения команды в пуле процессов.

        Args:
            future: Future объект завершенной команды.
            command_instance: Экземпляр выполненной команды.
        """
        if future.cancelled():
            self._logger.warning(
                f"Команда {type(command_instance).__name__} была отменена"
            )
            self._on_command_cancelled(command_instance)
        elif future.exception():
            exc = future.exception()
            self._logger.error(
                f"Ошибка при выполнении команды "
                f"{type(command_instance).__name__}: {exc}"
            )
            if isinstance(exc, Exception):
                self._on_command_error(exc, command_instance)
            else:
                # Преобразуем BaseException в Exception
                converted_exc = Exception(str(exc))
                self._on_command_error(converted_exc, command_instance)
        else:
            result = future.result()
            self._logger.info(
                f"Команда {type(command_instance).__name__} успешно завершена"
            )
            self._on_command_success(result, command_instance)

        self._clear_command_data()

    def _on_command_success(
        self, result: CommandResult, command_instance: NavigationCommand
    ) -> None:
        """Обрабатывает успешное завершение команды.

        Args:
            result: Результат выполнения команды.
            command_instance: Экземпляр выполненной команды.
        """
        if not result.success:
            self._logger.error(
                "Команда {name} завершилась с ошибкой".format(
                    name=type(command_instance).__name__
                )
            )
            raise RuntimeError(result.message)

        self._logger.info(
            "Команда завершена успешно: {msg}".format(msg=result.message)
        )

        command_type = type(command_instance).__name__

        if result.data is not None:
            self._logger.debug(
                "Кеширование данных команды: {}".format(result.data)
            )
            self._nav_cache.append(result.data)

        if command_type == "LandCommand":
            new_state = NavigationState.IDLE
        else:
            new_state = NavigationState.FLYING

        # Проверяем, можно ли перейти в новое состояние
        if new_state in self._transitions[self._current_state]:
            # Выполняем выход из текущего состояния
            self._execute_exit_method(self._current_state)

            self._logger.info(
                f"Переход из состояния {self._current_state.name} "
                f"в {new_state.name} после завершения команды"
            )

            # Просто меняем состояние без вызова _on_enter_*
            self._current_state = new_state

            # Только логируем вход в состояние, не запускаем команды
            self._logger.info(f"Дрон в состоянии {new_state.name}")
        else:
            self._logger.warning(
                f"Невозможно перейти из состояния {self._current_state.name} "
                f"в {new_state.name} после завершения команды"
            )

        self._clear_command_data()

    def _on_command_error(
        self, error: Exception, command_instance: NavigationCommand
    ) -> None:
        """Обрабатывает ошибку при выполнении команды.

        Args:
            error: Исключение, возникшее при выполнении команды.
            command_instance: Экземпляр команды, вызвавшей ошибку.
        """
        self._logger.error(
            f"Ошибка команды {type(command_instance).__name__}: {str(error)}"
        )

        self._clear_command_data()

        try:
            self.transition(NavigationState.EMERGENCY)
        except ValueError:
            self._logger.critical("Невозможно перейти в состояние EMERGENCY")

    def _on_command_cancelled(
        self, command_instance: NavigationCommand
    ) -> None:
        """Обрабатывает отмену команды.

        Args:
            command_instance: Экземпляр отмененной команды.
        """
        self._logger.info(
            f"Команда {type(command_instance).__name__} была отменена"
        )

    def _execute_enter_method(
        self, state: NavigationState, *args, **kwargs
    ) -> None:
        """Вызывает метод входа для заданного состояния.

        Args:
            state: Состояние, для которого нужно вызвать метод входа.
            *args: Позиционные аргументы для метода входа.
            **kwargs: Именованные аргументы для метода входа.
        """
        enter_method = getattr(self, f"_on_enter_{state.name.lower()}", None)
        if enter_method:
            self._logger.debug(f"Вход в состояние {state.name}")
            enter_method(*args, **kwargs)

    def _execute_exit_method(self, state: NavigationState) -> None:
        """Вызывает метод выхода для заданного состояния.

        Args:
            state: Состояние, для которого нужно вызвать метод выхода.
        """
        exit_method = getattr(self, f"_on_exit_{state.name.lower()}", None)
        if exit_method:
            exit_method()

    def _clear_command_data(self) -> None:
        """Очищает временные данные, связанные с выполненной командой."""
        if self._current_command and not self._current_command.done():
            self._current_command.cancel()

        self._current_command = None
        self._current_command_instance = None
        self._logger.debug("Временные данные команды очищены.")

    def _is_cpu_intensive_command(
        self, command_instance: NavigationCommand
    ) -> bool:
        """Определяет, является ли команда CPU-интенсивной.

        Args:
            command_instance: Экземпляр команды для проверки.

        Returns:
            True если команда требует выполнения в отдельном процессе.
        """
        # Только MoveCommand является CPU-интенсивной (планирование + MPPI)
        return type(command_instance).__name__ == "MoveCommand"

    def shutdown(self) -> None:
        """Корректно завершает работу машины состояний."""
        self._logger.info("Завершение работы NavigationStateMachine")

        if self._current_command and not self._current_command.done():
            self._logger.info("Отмена текущей команды")
            self._current_command.cancel()

        if self._process_pool:
            self._process_pool.shutdown(wait=True)
            self._process_pool = None

        self._clear_command_data()
        self._logger.info("NavigationStateMachine завершена")

    # Методы входа в состояния (on_enter_*)
    def _on_enter_idle(self) -> None:
        """Действия при входе в состояние IDLE."""
        self._logger.info("Дрон в состоянии ожидания (IDLE).")

    def _on_enter_flying(self) -> None:
        """Действия при входе в состояние FLYING."""
        self._logger.info("Дрон в состоянии полета (FLYING).")

    def _on_enter_takeoff(self, *args, **kwargs) -> None:
        """Действия при входе в состояние TAKEOFF."""
        self._logger.info("Дрон начинает взлет (TAKEOFF).")

        # Создаем и запускаем команду взлета
        from ara_api._core.services.nav.behavior.commands import TakeOffCommand

        self._logger.debug(
            f"Параметры команды взлета(_on_enter_takeoff): {kwargs}"
        )
        target_altitude = kwargs.get("target", None)
        takeoff_command = TakeOffCommand(target_altitude)
        self.handle_command(command_instance=takeoff_command, *args, **kwargs)

    def _on_enter_land(self, *args, **kwargs) -> None:
        """Действия при входе в состояние LAND."""
        self._logger.info("Дрон начинает посадку (LAND).")

        # Создаем и запускаем команду посадки
        from ara_api._core.services.nav.behavior.commands import LandCommand

        land_command = LandCommand()
        self.handle_command(command_instance=land_command, *args, **kwargs)

    def _on_enter_move(self, *args, **kwargs) -> None:
        """Действия при входе в состояние MOVE."""
        self._logger.info("Дрон начинает перемещение (MOVE).")

        # Создаем и запускаем команду перемещения
        from ara_api._core.services.nav.behavior.commands.cmd_move import (
            MoveCommand,
        )

        target_position = kwargs.get("target_position")
        if target_position is None:
            self._logger.error("Не указана целевая позиция для перемещения")
            return

        move_command = MoveCommand(target_position)
        self.handle_command(command_instance=move_command, *args, **kwargs)

    def _on_enter_speed(self, *args, **kwargs) -> None:
        """Действия при входе в состояние SPEED."""
        self._logger.info("Дрон изменяет скорость (SPEED).")

        # Создаем и запускаем команду изменения скорости
        from ara_api._core.services.nav.behavior.commands.cmd_speed import (
            SpeedCommand,
        )

        target_velocity = kwargs.get("target_velocity", (0.0, 0.0))

        speed_command = SpeedCommand(target_velocity)
        self.handle_command(command_instance=speed_command, *args, **kwargs)

    def _on_enter_altitude(self, *args, **kwargs) -> None:
        """Действия при входе в состояние ALTITUDE."""
        self._logger.info("Дрон изменяет высоту (ALTITUDE).")

        # Создаем и запускаем команду изменения высоты
        from ara_api._core.services.nav.behavior.commands.cmd_altitude import (
            AltitudeCommand,
        )

        target_altitude = kwargs.get("target_altitude")
        if target_altitude is None:
            self._logger.error("Не указана целевая высота")
            return

        altitude_command = AltitudeCommand(target_altitude)
        self.handle_command(command_instance=altitude_command, *args, **kwargs)

    def _on_enter_emergency(self) -> None:
        """Действия при входе в состояние EMERGENCY."""
        self._logger.warning("Дрон в аварийном состоянии (EMERGENCY).")

        # Отменяем текущую команду, если она выполняется
        if self._current_command and not self._current_command.done():
            self._logger.info(
                "Отмена текущей команды из-за аварийной ситуации"
            )
            self._current_command.cancel()
            self._clear_command_data()

    # Методы выхода из состояний (on_exit_*)
    def _on_exit_idle(self) -> None:
        """Действия при выходе из состояния IDLE."""
        self._logger.debug("Выход из состояния ожидания (IDLE).")

    def _on_exit_takeoff(self) -> None:
        """Действия при выходе из состояния TAKEOFF."""
        self._logger.debug("Выход из состояния взлета (TAKEOFF).")

    def _on_exit_flying(self) -> None:
        """Действия при выходе из состояния FLYING."""
        self._logger.debug("Выход из состояния полета (FLYING).")

    def _on_exit_land(self) -> None:
        """Действия при выходе из состояния LAND."""
        self._logger.debug("Выход из состояния посадки (LAND).")

    def _on_exit_move(self) -> None:
        """Действия при выходе из состояния MOVE."""
        self._logger.debug("Выход из состояния перемещения (MOVE).")

    def _on_exit_speed(self) -> None:
        """Действия при выходе из состояния SPEED."""
        self._logger.debug("Выход из состояния изменения скорости (SPEED).")

    def _on_exit_altitude(self) -> None:
        """Действия при выходе из состояния ALTITUDE."""
        self._logger.debug("Выход из состояния изменения высоты (ALTITUDE).")

    def _on_exit_emergency(self) -> None:
        """Действия при выходе из состояния EMERGENCY."""
        self._logger.debug("Выход из аварийного состояния (EMERGENCY).")

    @property
    def current_state(self) -> NavigationState:
        """Возвращает текущее состояние машины состояний.

        Returns:
            Текущее состояние навигации.
        """
        return self._current_state

    @property
    def is_command_running(self) -> bool:
        """Проверяет, выполняется ли в данный момент какая-либо команда.

        Returns:
            True если команда выполняется, False иначе.
        """
        return (
            self._current_command is not None
            and not self._current_command.done()
        )

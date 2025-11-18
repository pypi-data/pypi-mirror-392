from typing import Optional, Tuple

from ara_api._core.services.nav.behavior.commands._subutils import (
    CommandResult,
    NavigationCommand,
)
from ara_api._utils import RC, Logger, NavigationStateCached, gRPCSync
from ara_api._utils.config import SPEED_COMMAND


class SpeedCommand(NavigationCommand):
    """Команда установки скорости дрона.

    Управляет скоростью дрона в 2D плоскости (vx, vy) путем
    преобразования скоростей в соответствующие значения RC каналов.
    """

    def __init__(self, target: Optional[Tuple[float, float]] = None):
        """Инициализирует команду управления скоростью.

        Args:
            vx: Скорость по оси X (вперед/назад) в м/с.
            vy: Скорость по оси Y (влево/вправо) в м/с.
        """
        self._target = target if target is not None else (0.0, 0.0)
        self._grpc_sync = gRPCSync.get_instance()
        self._nav_cache = NavigationStateCached()
        self._logger = Logger(
            log_level=SPEED_COMMAND.LOG_LEVEL,
            log_to_file=SPEED_COMMAND.LOG_TO_FILE,
            log_to_terminal=SPEED_COMMAND.LOG_TO_TERMINAL,
        )
        self.rc_command = RC()

    def can_execute(self, *args, **kwargs) -> bool:
        """Проверяет возможность установки скорости.

        Returns:
            True если можно установить скорость, False иначе.
        """
        try:
            # Простая проверка доступности gRPC соединения
            # if not kwargs.get("source") == "test-cmd":
            #     current_altitude = self._grpc_sync.msp_get_altitude()
            #     if current_altitude is None:
            #         self._logger.error(
            #             "[SPEED]: Не удалось получить текущую высоту"
            #         )
            #         return False

            # Проверяем разумные пределы скорости
            if (
                abs(self._target[0]) > SPEED_COMMAND.MAX_LINEAR_SPEED
                or abs(self._target[1]) > SPEED_COMMAND.MAX_LINEAR_SPEED
            ):
                self._logger.error(
                    f"[SPEED]: Слишком высокая скорость: vx={self._target[0]}, "
                    f" vy={self._target[1]} "
                    f"(максимум: ±{SPEED_COMMAND.MAX_LINEAR_SPEED} м/с)"
                )
                return False

            return True

        except Exception as e:
            self._logger.error(
                f"[SPEED]: Ошибка при проверке возможности установки скорости: {e}"
            )
            return False

    def execute(self, *args, **kwargs) -> CommandResult:
        """Выполняет команду установки скорости.

        Returns:
            Результат выполнения команды установки скоростиCal
        """
        try:
            self._logger.info(
                f"[SPEED]: Установка скорости: vx={self._target[0]:.2f} м/с, "
                f"vy={self._target[1]:.2f} м/с"
            )

            last_cmd = self._nav_cache.get_last()
            self._logger.debug(
                "[SPEED]: Полученные данные из Cache: {}".format(last_cmd)
            )

            rc_command = last_cmd.get("rc_command", {})
            self._logger.debug(
                f"[SPEED]: Текущая команда RC из Cache: {rc_command}"
            )

            self.rc_command.transform_from_vel(
                self._target[0], self._target[1], 0, 0
            )
            self.rc_command.grpc.thr = rc_command.grpc.thr
            self.rc_command.grpc.rud = rc_command.grpc.rud

            self._logger.debug(
                f"[SPEED]: Сконвертированная команда по скорости {self.rc_command}"
            )

            # Отправляем команду RC через gRPC
            if not kwargs.get("source") == "test-cmd":
                self._grpc_sync.msp_cmd_send_rc(self.rc_command.grpc, None)

            return CommandResult(
                success=True,
                message=f"Скорость установлена: vx={self._target[0]:.2f} м/с, "
                f"vy={self._target[1]:.2f} м/с",
                data={
                    "cmd": "speed",
                    "target_altitude": last_cmd.get("target_altitude", {}),
                    "rc_command": self.rc_command,
                },
            )

        except Exception as e:
            error_msg = f"Ошибка при установке скорости: {e}"
            self._logger.error(error_msg)
            return CommandResult(
                success=False, message=error_msg, data={"error": str(e)}
            )

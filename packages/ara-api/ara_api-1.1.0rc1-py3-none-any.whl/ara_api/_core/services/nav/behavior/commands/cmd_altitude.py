"""Команда управления высотой дрона."""

import logging

from ara_api._core.services.nav.behavior.commands._subutils import (
    CommandResult,
    NavigationCommand,
)
from ara_api._utils.communication.grpc_sync import gRPCSync
from ara_api._utils.data.msp import RC, Altitude


class AltitudeCommand(NavigationCommand):
    """Команда установки высоты дрона.

    Управляет высотой дрона путем модификации throttle в зависимости
    от разности между текущей и целевой высотой.
    """

    def __init__(self, target_altitude: Altitude):
        """Инициализирует команду управления высотой.

        Args:
            target_altitude: Целевая высота в виде объекта Altitude.
        """
        self._target_altitude = target_altitude
        self._grpc_sync = gRPCSync.get_instance()
        self._logger = logging.getLogger(__name__)

    def can_execute(self, *args, **kwargs) -> bool:
        """Проверяет возможность установки высоты.

        Returns:
            True если можно изменить высоту, False иначе.
        """
        try:
            # Простая проверка доступности gRPC соединения
            # current_altitude = self._grpc_sync.msp_get_altitude()
            # if current_altitude is None:
            #     self._logger.error("Не удалось получить текущую высоту")
            #     return False

            # Проверяем разумные пределы высоты
            target_alt = self._target_altitude.grpc.data
            if target_alt < 0.1 or target_alt > 50.0:
                self._logger.error(
                    f"Недопустимая целевая высота: {target_alt}м "
                    f"(допустимо: 0.1-50.0м)"
                )
                return False

            return True

        except Exception as e:
            self._logger.error(
                f"Ошибка при проверке возможности изменения высоты: {e}"
            )
            return False

    def execute(self, *args, **kwargs) -> CommandResult:
        """Выполняет команду изменения высоты.

        Returns:
            Результат выполнения команды изменения высоты.
        """
        try:
            # Получаем текущую высоту
            current_altitude = self._grpc_sync.msp_get_altitude()
            if current_altitude is None:
                return CommandResult(
                    success=False,
                    message="Не удалось получить текущую высоту",
                )

            current_alt = current_altitude.grpc.data
            target_alt = self._target_altitude.grpc.data

            self._logger.info(
                f"Изменение высоты с {current_alt:.2f}м на {target_alt:.2f}м"
            )

            # Вычисляем разность высот
            altitude_diff = target_alt - current_alt

            # Определяем throttle на основе разности высот
            # Используем пропорциональное управление
            kp = 300.0  # Коэффициент пропорциональности
            throttle_adjustment = int(kp * altitude_diff)

            # Базовый throttle для удержания высоты (hover)
            base_throttle = 1500

            # Рассчитываем новый throttle
            new_throttle = base_throttle + throttle_adjustment

            # Ограничиваем throttle допустимыми значениями
            new_throttle = max(1000, min(2000, new_throttle))

            # Создаем RC команду
            rc_command = RC()
            rc_command.grpc.ail = 1500  # Нейтральная позиция (roll)
            rc_command.grpc.ele = 1500  # Нейтральная позиция (pitch)
            rc_command.grpc.rud = 1500  # Нейтральная позиция (yaw)
            rc_command.grpc.thr = new_throttle  # throttle

            # Обновляем JSON представление
            rc_command.json["rc"] = [
                rc_command.grpc.ail,
                rc_command.grpc.ele,
                rc_command.grpc.thr,
                rc_command.grpc.rud,
                1000,
                1000,
                1000,
                1000,  # aux каналы
            ]

            # Отправляем команду RC через gRPC
            self._grpc_sync.msp_cmd_send_rc(rc_command.grpc, None)

            self._logger.info(
                f"Команда высоты отправлена: throttle={new_throttle}, "
                f"diff={altitude_diff:.2f}м"
            )

            return CommandResult(
                success=True,
                message=f"Высота изменена на {target_alt:.2f}м",
                data={
                    "current_altitude": current_alt,
                    "target_altitude": target_alt,
                    "altitude_diff": altitude_diff,
                    "throttle": new_throttle,
                    "rc_command": rc_command.json,
                },
            )

        except Exception as e:
            error_msg = f"Ошибка при изменении высоты: {e}"
            self._logger.error(error_msg)
            return CommandResult(
                success=False, message=error_msg, data={"error": str(e)}
            )

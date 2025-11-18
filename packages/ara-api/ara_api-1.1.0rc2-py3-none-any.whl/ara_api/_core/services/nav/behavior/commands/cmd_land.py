import time
from typing import Any, List, Optional

import numpy as np
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from ara_api._core.services.nav.behavior.commands._subutils import (
    CommandResult,
    NavigationCommand,
)
from ara_api._utils import (
    RC,
    Altitude,
    Logger,
    NavigationStateCached,
    gRPCSync,
)
from ara_api._utils.config import LAND_COMMAND


class LandCommand(NavigationCommand):
    """Команда посадки дрона.

    Выполняет плавную посадку дрона с помощью постепенного уменьшения
    throttle до минимального значения.
    """

    def __init__(self):
        """Инициализирует команду посадки.

        Args:
            landing_throttle: Значение throttle для посадки (1000-1100).
        """
        self._grpc_sync = gRPCSync.get_instance()
        self._nav_cache = NavigationStateCached()
        self._logger = Logger(
            log_level=LAND_COMMAND.LOG_LEVEL,
            log_to_file=LAND_COMMAND.LOG_TO_FILE,
            log_to_terminal=LAND_COMMAND.LOG_TO_TERMINAL,
        )
        self._logger.debug("[LAND]: Инициализация команды посадки")
        self.rc_command = RC()

    def can_execute(self, *args, **kwargs) -> bool:
        """Проверяет возможность выполнения посадки.

        Returns:
            True если дрон может совершить посадку, False иначе.
        """
        try:
            # Простая проверка доступности gRPC соединения
            # if not kwargs.get("source") == "test-cmd":
            #     current_altitude = self._grpc_sync.msp_get_altitude()
            #     if current_altitude is None:
            #         self._logger.error(
            #             "[LAND]: Не удалось получить текущую высоту"
            #         )
            #         return False

            return True

        except Exception as e:
            self._logger.error(
                f"[LAND]: Ошибка при проверке возможности посадки: {e}"
            )
            return False

    def execute(self, *args, **kwargs) -> CommandResult:
        """Выполняет команду посадки.

        Returns:
            Результат выполнения команды посадки.
        """
        try:
            last_cmd = self._nav_cache.get_last()
            self._logger.debug(
                "[LAND]: Полученные данные из Cache: {}".format(last_cmd)
            )

            target_altitude = last_cmd.get("target_altitude", {}).alt
            rc_command_thr = last_cmd.get("rc_command", {}).grpc.thr

            throttle_values = self._expo(target_altitude, rc_command_thr)[::-1]
            self._logger.debug(
                f"[LAND]: Сгенерированные значения throttle: {throttle_values}"
            )
            self._logger.debug(
                "[LAND]: Диапазон throttle: {first}:{second}, "
                "количество шагов: {length}".format(
                    first=throttle_values[0],
                    second=throttle_values[-1],
                    length=len(throttle_values),
                )
            )

            progress = Progress(
                SpinnerColumn(style="bold blue"),
                TextColumn("[bold blue]Посадка"),
                BarColumn(bar_width=50, style="blue", complete_style="green"),
                MofNCompleteColumn(),
                TextColumn("[bold green]Throttle: {task.fields[throttle]}"),
                TimeElapsedColumn(),
            )

            with Live(
                Panel(
                    progress,
                    title="[bold] ARA API - Посадка[/bold]",
                    style="blue",
                    title_align="center",
                ),
                refresh_per_second=4,
            ) as live:
                task = progress.add_task(
                    "land",
                    total=len(throttle_values),
                    throttle=throttle_values[0],
                )

                for i, throttle in enumerate(throttle_values):
                    self.rc_command.grpc.thr = throttle

                    # Обновляем прогресс бар с текущим throttle
                    progress.update(task, advance=1, throttle=throttle)

                    if not kwargs.get("source") == "test-cmd":
                        self._grpc_sync.msp_cmd_send_rc(
                            self.rc_command.grpc, None
                        )
                    time.sleep(LAND_COMMAND.TIME_DELAY)

            return CommandResult(
                success=True,
                message="Посадка инициирована",
                data={
                    "cmd": "land",
                    "landing_throttle": throttle_values[-1],
                    "rc_command": self.rc_command,
                },
            )

        except Exception as e:
            error_msg = f"Ошибка при выполнении посадки: {e}"
            self._logger.error(error_msg)
            return CommandResult(
                success=False, message=error_msg, data={"error": str(e)}
            )

    def _expo(self, current_altitude: int, mapped_altitude: int) -> List[int]:
        steps = max(
            5,
            int((current_altitude * 10) / LAND_COMMAND.TIME_DELAY),
        )

        self._logger.debug(
            f"[LAND]: Сгенерировано {steps} шагов для посадки до высоты "
            f"со сконвертированной высотой {current_altitude}"
        )

        t = np.linspace(0, 1, steps)
        expo = np.exp(LAND_COMMAND.EXPONENT * t) - 1
        max_expo = np.exp(LAND_COMMAND.EXPONENT) - 1

        normalized_expo = expo / max_expo
        return (1000 + normalized_expo * (mapped_altitude - 1000)).astype(int)

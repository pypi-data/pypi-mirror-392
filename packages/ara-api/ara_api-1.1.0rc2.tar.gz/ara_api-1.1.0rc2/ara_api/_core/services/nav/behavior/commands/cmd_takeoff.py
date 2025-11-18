import time
from typing import Any, Optional

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
from ara_api._utils.config import TAKEOFF_COMMAND


class TakeOffCommand(NavigationCommand):
    """Команда взлета дрона.

    Выполняет взлет дрона до заданной высоты с помощью управления
    throttle через RC-каналы.
    """

    def __init__(self, target: Optional[float] = None):
        """Инициализирует команду взлета.

        Args:
            target_altitude: Целевая высота взлета в метрах.
                           Если None, используется значение по умолчанию
                           из конфигурации.
        """
        self._target_altitude = Altitude(
            target if target is not None else TAKEOFF_COMMAND.DEFAULT_ALTITUDE
        )
        self._grpc_sync = gRPCSync.get_instance()
        self._nav_cache = NavigationStateCached()
        self._logger = Logger(
            log_level=TAKEOFF_COMMAND.LOG_LEVEL,
            log_to_file=TAKEOFF_COMMAND.LOG_TO_FILE,
            log_to_terminal=TAKEOFF_COMMAND.LOG_TO_TERMINAL,
        )
        self._logger.debug(
            f"[TAKEOFF]: Инициализация команды взлета с высотой {self._target_altitude}м"
        )
        self.rc_command = RC()

    def can_execute(self, *args, **kwargs) -> bool:
        """Проверяет возможность выполнения взлета.

        Returns:
            True если дрон может взлететь, False иначе.
        """
        try:
            # if not kwargs.get("source") == "test-cmd":
            #     # Простая проверка доступности gRPC соединения
            #     current_altitude = self._grpc_sync.msp_get_altitude()
            #     if current_altitude is None:
            #         self._logger.error(
            #             "[TAKEOFF]: Не удалось получить текущую высоту"
            #         )
            #         return False

            # Проверяем разумные пределы целевой высоты
            if (
                self._target_altitude.alt < TAKEOFF_COMMAND.MIN_ALTITUDE
                or self._target_altitude.alt > TAKEOFF_COMMAND.MAX_ALTITUDE
            ):
                self._logger.error(
                    f"[TAKEOFF]: Недопустимая целевая высота: {self._target_altitude}м"
                )
                return False

            return True

        except Exception as e:
            self._logger.error(
                f"[TAKEOFF]: Ошибка при проверке возможности взлета: {e}"
            )
            return False

    def execute(self, *args, **kwargs) -> CommandResult:
        """Выполняет команду взлета.

        Returns:
            Результат выполнения команды взлета.
        """
        try:
            self._logger.info(
                f"[TAKEOFF]: Начинаем взлет до высоты {self._target_altitude.alt} м"
            )

            throttle_values = self._expo()
            self._logger.debug(
                f"[TAKEOFF]: Сгенерированные значения throttle: {throttle_values}"
            )
            self._logger.debug(
                "[TAKEOFF]: Диапазон throttle: {first}:{second}, "
                "количество шагов: {length}".format(
                    first=throttle_values[0],
                    second=throttle_values[-1],
                    length=len(throttle_values),
                )
            )

            progress = Progress(
                SpinnerColumn(style="bold blue"),
                TextColumn(
                    "[bold blue]Взлет до {altitude}м".format(
                        altitude=self._target_altitude.alt
                    )
                ),
                BarColumn(bar_width=50, style="blue", complete_style="green"),
                MofNCompleteColumn(),
                TextColumn("[bold green]Throttle: {task.fields[throttle]}"),
                TimeElapsedColumn(),
            )

            with Live(
                Panel(
                    progress,
                    title="[bold] ARA API - Взлет[/bold]",
                    style="blue",
                    title_align="center",
                ),
                refresh_per_second=4,
            ) as live:
                task = progress.add_task(
                    "takeoff",
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
                    time.sleep(TAKEOFF_COMMAND.TIME_DELAY)

            return CommandResult(
                success=True,
                message=(
                    f"Взлет инициирован до высоты {self._target_altitude.alt} м"
                ),
                data={
                    "cmd": "takeoff",
                    "target_altitude": self._target_altitude,
                    "rc_command": self.rc_command,
                },
            )

        except Exception as e:
            error_msg = f"Ошибка при выполнении взлета: {e}"
            self._logger.error(error_msg)
            return CommandResult(
                success=False, message=error_msg, data={"error": str(e)}
            )

    def _expo(self) -> list:
        mapped_altitude = int(
            self._target_altitude.map(
                from_min=TAKEOFF_COMMAND.MIN_ALTITUDE,
                from_max=TAKEOFF_COMMAND.MAX_ALTITUDE,
                to_min=1000,
                to_max=2000,
            )
        )
        steps = max(
            5,
            int((self._target_altitude.alt * 10) / TAKEOFF_COMMAND.TIME_DELAY),
        )

        self._logger.debug(
            f"[TAKEOFF]: Сгенерировано {steps} шагов для взлета до высоты "
            f"{self._target_altitude.alt}м со сконвертированной высотой "
            f"{mapped_altitude}"
        )

        t = np.linspace(0, 1, steps)
        expo = np.exp(TAKEOFF_COMMAND.EXPONENT * t) - 1
        max_expo = np.exp(TAKEOFF_COMMAND.EXPONENT) - 1

        normalized_expo = expo / max_expo
        return (1000 + normalized_expo * (mapped_altitude - 1000)).astype(int)

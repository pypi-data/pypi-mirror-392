import time
from typing import Dict

from ara_api._core.services.msp.telemetry.telemetry_registry import (
    TelemetryRegistry,
)
from ara_api._utils import Logger


class TelemetryScheduler:
    def __init__(
        self, registry: TelemetryRegistry, base_freq: int = 50
    ) -> None:
        self.registry = registry
        self.base_freq = base_freq
        self.interval = 1.0 / base_freq
        self._counters: Dict[str, int] = {}
        self._running = False
        self.logger = Logger(log_to_file=True, log_to_terminal=True)

    def start(self) -> None:
        self._running = True
        self._counters = {
            reader.get_name(): 0 for reader, _ in self.registry.get_all()
        }
        self.logger.info("[TelemetryScheduler] Started")

    def stop(self) -> None:
        self._running = False
        self.logger.info("[TelemetryScheduler] Stopped")

    def update_cycle(self) -> None:
        if not self._running:
            return

        cycle_start = time.time()

        for reader, frequency in self.registry.get_all():
            name = reader.get_name()

            try:
                self._counters[name] += 1

                if self._counters[name] >= frequency:
                    self._counters[name] = 0

                    result = reader.read()
                    data_obj = reader.get_data_object()

                    if data_obj is not None and result is not None:
                        try:
                            data_obj.sync(result)
                        except Exception as e:
                            self.logger.warning(f"Sync error for {name}: {e}")
            except Exception as e:
                self.logger.error(f"Error processing {name}: {e}")

        elapsed = time.time() - cycle_start
        sleep_time = max(0, self.interval - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

    def is_running(self) -> bool:
        return self._running

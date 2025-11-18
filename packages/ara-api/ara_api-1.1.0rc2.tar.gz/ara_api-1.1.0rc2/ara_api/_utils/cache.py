import os
import threading
from collections import deque
from typing import Any, ClassVar, Dict

from ara_api._utils.config import LOGGER_CONFIG
from ara_api._utils.logger import Logger


class NavigationStateCached:
    _instance: ClassVar[Dict[int, "NavigationStateCached"]] = {}
    _creation_lock: ClassVar[threading.Lock] = threading.Lock()
    _logger: ClassVar[Logger] = Logger(
        log_level=LOGGER_CONFIG.LOG_LEVEL,
        log_to_file=LOGGER_CONFIG.LOG_TO_FILE,
        log_to_terminal=LOGGER_CONFIG.LOG_TO_TERMINAL,
        log_dir=LOGGER_CONFIG.LOG_DIR,
    )

    def __new__(cls) -> "NavigationStateCached":
        process_id = os.getpid()

        if process_id not in cls._instance:
            with cls._creation_lock:
                if process_id not in cls._instance:
                    instance = super().__new__(cls)
                    cls._instance[process_id] = instance
                    cls._logger.debug(
                        "NavigationStateCached instance created"
                        " process ID: {}".format(process_id)
                    )

        return cls._instance[process_id]

    def __init__(self):
        if hasattr(self, "_initialized"):
            self._logger.debug(
                "Navigation State Cache "
                "already initialized for process ID: {id}".format(
                    id=os.getpid()
                )
            )
            return

        self._cache_last_cmd: deque[Any] = deque(maxlen=20)
        self._initialized = True

    def get_last(self) -> dict:
        return self._cache_last_cmd[-1]

    def append(self, value: Any):
        self._cache_last_cmd.append(value)

    def count(self, value: Any) -> int:
        return self._cache_last_cmd.count(value)

    def clear(self):
        self._cache_last_cmd.clear()

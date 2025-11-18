import time
from typing import Union

from ara_api._utils import (
    Logger,
    SerialTransmitter,
    TCPTransmitter,
    Transmitter,
)


class ConnectionManager:

    def __init__(
        self,
        mode: str,
        link: Union[tuple, str],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.mode = mode
        self.link = link
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = Logger(log_to_file=True, log_to_terminal=True)
        self.transmitter = self._create_transmitter()

    def _create_transmitter(self) -> Transmitter:
        if self.mode == "TCP":
            if not isinstance(self.link, tuple):
                raise ValueError(
                    f"TCP mode requires tuple link, got {type(self.link)}"
                )
            return TCPTransmitter(self.link)
        elif self.mode == "SERIAL":
            if not isinstance(self.link, str):
                raise ValueError(
                    f"SERIAL mode requires string link, got {type(self.link)}"
                )
            return SerialTransmitter(self.link, 115200)
        else:
            raise ValueError(
                f"Unknown mode: {self.mode}. Use 'TCP' or 'SERIAL'"
            )

    def connect(self) -> bool:
        try:
            if self.transmitter.connect():
                self.logger.info(
                    f"[ConnectionManager] Connected via {self.mode}"
                )
                return True
            else:
                self.logger.error(
                    "[ConnectionManager] Failed to connect"
                )
                return False
        except Exception as e:
            self.logger.error(
                f"[ConnectionManager] Connection error: {e}"
            )
            return False

    def reconnect(self) -> bool:
        for attempt in range(self.max_retries):
            self.logger.info(
                f"[ConnectionManager] Reconnect attempt "
                f"{attempt + 1}/{self.max_retries}"
            )

            if self.connect():
                return True

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (2**attempt))

        self.logger.error(
            "[ConnectionManager] Failed to reconnect "
            f"after {self.max_retries} attempts"
        )
        return False

    def disconnect(self) -> None:
        try:
            self.transmitter.close()
            self.logger.info("[ConnectionManager] Disconnected")
        except Exception as e:
            self.logger.error(
                f"[ConnectionManager] Disconnect error: {e}"
            )

    def get_transmitter(self) -> Transmitter:
        return self.transmitter

    def is_connected(self) -> bool:
        return self.transmitter.is_connected()

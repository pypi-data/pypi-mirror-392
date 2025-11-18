from typing import Dict, List, Optional, Tuple

from ara_api._core.services.msp.telemetry.telemetry_reader import (
    TelemetryReader,
)


class TelemetryRegistry:

    def __init__(self) -> None:
        self._readers: Dict[str, Tuple[TelemetryReader, int]] = {}

    def register(self, reader: TelemetryReader, frequency: int) -> None:
        name = reader.get_name()
        self._readers[name] = (reader, frequency)

    def unregister(self, name: str) -> None:
        if name in self._readers:
            del self._readers[name]

    def get_all(self) -> List[Tuple[TelemetryReader, int]]:
        return list(self._readers.values())

    def get_reader(self, name: str) -> Optional[TelemetryReader]:
        entry = self._readers.get(name)
        return entry[0] if entry else None

    def get_frequency(self, name: str) -> Optional[int]:
        entry = self._readers.get(name)
        return entry[1] if entry else None

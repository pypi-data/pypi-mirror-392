from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class TelemetryReader(ABC):

    @abstractmethod
    def read(self) -> Any:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_data_object(self) -> Any:
        pass

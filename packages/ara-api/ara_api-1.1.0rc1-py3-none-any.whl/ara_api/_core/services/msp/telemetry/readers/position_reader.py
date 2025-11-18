from typing import Any

from ara_api._core.services.msp.controller import MSPController
from ara_api._core.services.msp.telemetry.telemetry_reader import (
    TelemetryReader,
)
from ara_api._utils.data.msp import Position


class PositionReader(TelemetryReader):

    def __init__(
        self, controller: MSPController, data_object: Position
    ) -> None:
        self.controller = controller
        self.data_object = data_object

    def read(self) -> Any:
        return self.controller.msp_read_pos_est_data()

    def get_name(self) -> str:
        return "POSITION"

    def get_data_object(self) -> Position:
        return self.data_object

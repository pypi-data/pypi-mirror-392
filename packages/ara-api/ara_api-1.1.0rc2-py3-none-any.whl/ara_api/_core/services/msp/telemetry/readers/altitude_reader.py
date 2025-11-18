from typing import Any

from ara_api._core.services.msp.controller import MSPController
from ara_api._core.services.msp.telemetry.telemetry_reader import (
    TelemetryReader,
)
from ara_api._utils.data.msp import Altitude


class AltitudeReader(TelemetryReader):

    def __init__(
        self, controller: MSPController, data_object: Altitude
    ) -> None:
        self.controller = controller
        self.data_object = data_object

    def read(self) -> Any:
        return self.controller.msp_read_altitude_data()

    def get_name(self) -> str:
        return "ALTITUDE"

    def get_data_object(self) -> Altitude:
        return self.data_object

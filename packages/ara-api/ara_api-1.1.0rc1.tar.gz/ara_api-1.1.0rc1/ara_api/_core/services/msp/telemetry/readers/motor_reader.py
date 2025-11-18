from typing import Any

from ara_api._core.services.msp.controller import MSPController
from ara_api._core.services.msp.telemetry.telemetry_reader import (
    TelemetryReader,
)
from ara_api._utils.data.msp import Motor


class MotorReader(TelemetryReader):

    def __init__(
        self, controller: MSPController, data_object: Motor
    ) -> None:
        self.controller = controller
        self.data_object = data_object

    def read(self) -> Any:
        return self.controller.msp_read_motor_data()

    def get_name(self) -> str:
        return "MOTOR"

    def get_data_object(self) -> Motor:
        return self.data_object

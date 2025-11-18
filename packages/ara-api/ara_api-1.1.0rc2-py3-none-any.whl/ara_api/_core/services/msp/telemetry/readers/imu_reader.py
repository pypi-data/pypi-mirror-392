from typing import Any

from ara_api._core.services.msp.controller import MSPController
from ara_api._core.services.msp.telemetry.telemetry_reader import (
    TelemetryReader,
)
from ara_api._utils.data.msp import IMU


class IMUReader(TelemetryReader):

    def __init__(
        self, controller: MSPController, data_object: IMU
    ) -> None:
        self.controller = controller
        self.data_object = data_object

    def read(self) -> Any:
        return self.controller.msp_read_imu_data()

    def get_name(self) -> str:
        return "IMU"

    def get_data_object(self) -> IMU:
        return self.data_object

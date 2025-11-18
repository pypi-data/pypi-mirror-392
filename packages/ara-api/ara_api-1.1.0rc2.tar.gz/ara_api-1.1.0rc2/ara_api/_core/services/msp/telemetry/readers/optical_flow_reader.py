from typing import Any

from ara_api._core.services.msp.controller import MSPController
from ara_api._core.services.msp.telemetry.telemetry_reader import (
    TelemetryReader,
)
from ara_api._utils.data.msp import OpticalFlow


class OpticalFlowReader(TelemetryReader):

    def __init__(
        self, controller: MSPController, data_object: OpticalFlow
    ) -> None:
        self.controller = controller
        self.data_object = data_object

    def read(self) -> Any:
        return self.controller.msp_read_optical_flow_data()

    def get_name(self) -> str:
        return "OPTICAL_FLOW"

    def get_data_object(self) -> OpticalFlow:
        return self.data_object

"""Analog sensor data class"""

from dataclasses import dataclass, field
from typing import Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    analog_data as analog_grpc,
)


@dataclass
class Analog:
    grpc: analog_grpc = field(default_factory=lambda: analog_grpc())
    json: dict = field(
        default_factory=lambda: {
            "vbat": 0.0,
            "current": 0.0,
            "rssi": 0,
            "airspeed": 0.0,
        }
    )

    def __repr__(self):
        return (
            "Analog(voltage={voltage}, amperage={amperage}, "
            "rssi={rssi}, mAhdrawn={mAhdrawn})".format(
                voltage=self.grpc.voltage,
                amperage=self.grpc.amperage,
                rssi=self.grpc.rssi,
                mAhdrawn=self.grpc.mAhdrawn,
            )
        )

    @overload
    def sync(self, grpc: analog_grpc) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(self, data: Union[analog_grpc, dict]) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC analog object or a JSON dictionary
        """
        if isinstance(data, analog_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON (using consistent field names from default)
            self.json["vbat"] = data.voltage
            self.json["current"] = data.amperage
            self.json["rssi"] = data.rssi
            # Note: airspeed is not provided by gRPC, keeping existing value

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json = data

            # Update gRPC (using consistent field names from default)
            self.grpc.voltage = data.get("vbat", 0.0)
            self.grpc.amperage = data.get("current", 0.0)
            self.grpc.rssi = data.get("rssi", 0)
            # Note: mAhdrawn not in default JSON structure

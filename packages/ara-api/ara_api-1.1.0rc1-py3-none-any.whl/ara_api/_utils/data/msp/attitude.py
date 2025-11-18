"""Attitude data class"""

from dataclasses import dataclass, field
from typing import Tuple, Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    attitude_data as attitude_grpc,
)


@dataclass
class Attitude:
    grpc: attitude_grpc = field(default_factory=lambda: attitude_grpc())
    json: dict = field(
        default_factory=lambda: {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
    )

    def __repr__(self):
        return "Attitude(roll={x}, pitch={y}, yaw={z})".format(
            x=self.grpc.data.x, y=self.grpc.data.y, z=self.grpc.data.z
        )

    @overload
    def sync(self, grpc: attitude_grpc) -> None: ...

    @overload
    def sync(self, data: Tuple[float, float, float]) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(
        self, data: Union[attitude_grpc, Tuple[float, float, float], dict]
    ) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC attitude object, a tuple of
            (roll,pitch,yaw), or a JSON dictionary
        """
        if isinstance(data, attitude_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            self.json["roll"] = data.data.x
            self.json["pitch"] = data.data.y
            self.json["yaw"] = data.data.z

        elif isinstance(data, tuple) and len(data) == 3:
            # Update from tuple (roll,pitch,yaw)
            self.grpc.data.x, self.grpc.data.y, self.grpc.data.z = data

            # Update JSON
            self.json["roll"], self.json["pitch"], self.json["yaw"] = data

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json = data

            # Update gRPC (using correct field names: data.x, data.y, data.z)
            self.grpc.data.x = data.get("roll", 0.0)
            self.grpc.data.y = data.get("pitch", 0.0)
            self.grpc.data.z = data.get("yaw", 0.0)

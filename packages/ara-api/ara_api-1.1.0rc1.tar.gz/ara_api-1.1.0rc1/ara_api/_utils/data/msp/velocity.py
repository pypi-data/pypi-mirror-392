"""Velocity data class"""

from dataclasses import dataclass, field
from typing import Tuple, Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    velocity_data,
)


@dataclass
class Velocity:
    grpc: velocity_data = field(default_factory=lambda: velocity_data())
    json: dict = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})

    def __repr__(self):
        return "Velocity(x={x}, y={y}, z={z})".format(
            x=self.grpc.data.x, y=self.grpc.data.y, z=self.grpc.data.z
        )

    @overload
    def sync(self, grpc: velocity_data) -> None: ...

    @overload
    def sync(self, data: Tuple[float, float, float]) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(
        self, data: Union[velocity_data, Tuple[float, float, float], dict]
    ) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC position object, a tuple of (x,y,z),
                  or a JSON dictionary
        """
        if isinstance(data, velocity_data):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            self.json["x"] = data.data.x
            self.json["y"] = data.data.y
            self.json["z"] = data.data.z

        elif isinstance(data, tuple) and len(data) == 3:
            # Update from tuple (x,y,z)
            self.grpc.data.x, self.grpc.data.y, self.grpc.data.z = data

            # Update JSON
            self.json["x"], self.json["y"], self.json["z"] = data

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json = data

            # Update gRPC
            self.grpc.data.x = data.get("x", 0.0)
            self.grpc.data.y = data.get("y", 0.0)
            self.grpc.data.z = data.get("z", 0.0)

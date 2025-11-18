"""Sonar data class"""

from dataclasses import dataclass, field
from typing import Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    sonar_data as sonar_grpc,
)


@dataclass
class Sonar:
    grpc: sonar_grpc = field(default_factory=lambda: sonar_grpc())
    json: dict = field(default_factory=lambda: {"distance": 0.0})

    def __repr__(self):
        return "Sonar(distance={sonar})".format(sonar=self.grpc.data)

    @overload
    def sync(self, grpc: sonar_grpc) -> None: ...

    @overload
    def sync(self, data: float) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(self, data: Union[sonar_grpc, float, dict]) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC sonar object, a tuple of
            (distance,confidence), or a JSON dictionary
        """
        if isinstance(data, sonar_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            self.json["distance"] = data.data

        elif isinstance(data, float):
            # Update from tuple (distance,confidence)
            self.grpc.data = data

            # Update JSON
            self.json["distance"] = data

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json = data

            # Update gRPC
            self.grpc.data = data.get("distance", 0.0)

"""Altitude data class"""

from dataclasses import dataclass, field
from typing import Tuple, Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    altitude_data as altitude_grpc,
)


@dataclass
class Altitude:
    alt: float = 0.0
    grpc: altitude_grpc = field(default_factory=lambda: altitude_grpc())
    json: dict = field(
        default_factory=lambda: {"altitude": 0.0, "variance": 0.0}
    )

    def __repr__(self):
        return "Altitude(altitude={alt})".format(alt=self.grpc.data)

    def __post_init__(self):
        # Initialize gRPC with the altitude value
        self.grpc.data = self.alt
        self.json["altitude"] = self.alt

    @overload
    def sync(self, grpc: altitude_grpc) -> None: ...

    @overload
    def sync(self, data: Tuple[float, float]) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(
        self, data: Union[altitude_grpc, Tuple[float, float], dict]
    ) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC altitude object, a tuple of
            (altitude,variance), or a JSON dictionary
        """
        if isinstance(data, altitude_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            self.json["altitude"] = data.data

        elif isinstance(data, tuple) and len(data) == 2:
            # Update from tuple (altitude,variance)
            self.grpc.data = data[0]  # altitude

            # Update JSON
            self.json["altitude"] = data[0]  # altitude
            self.json["variance"] = data[1]  # variance

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json = data

            # Update gRPC
            self.grpc.data = data.get("altitude", 0.0)

    def map(
        self,
        from_min: float,
        from_max: float,
        to_min: int,
        to_max: int,
    ) -> float:
        """
        Map a value from one range to another with linear interpolation.
        """
        value = max(from_min, min(from_max, self.alt))  # Clamp value

        from_span = from_max - from_min
        to_span = to_max - to_min

        value_scaled = (value - from_min) / from_span

        final_value = to_min + (value_scaled * to_span)

        return final_value

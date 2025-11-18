"""Optical Flow data class"""

from dataclasses import dataclass, field
from typing import Tuple, Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    optical_flow_data as optical_flow_grpc,
)


@dataclass
class OpticalFlow:
    grpc: optical_flow_grpc = field(
        default_factory=lambda: optical_flow_grpc()
    )
    json: dict = field(
        default_factory=lambda: {
            "flow": {"x": 0.0, "y": 0.0},
            "body": {"x": 0.0, "y": 0.0},
            "quality": 0,
        }
    )

    def __repr__(self):
        return (
            "OpticalFlow(flow=({flow_x}, {flow_y}),"
            "body=({body_x}, {body_y}), quality={quality})".format(
                flow_x=self.grpc.flow_rate.x,
                flow_y=self.grpc.flow_rate.y,
                body_x=self.grpc.body_rate.x,
                body_y=self.grpc.body_rate.y,
                quality=self.grpc.quality,
            )
        )

    @overload
    def sync(self, grpc: optical_flow_grpc) -> None: ...

    @overload
    def sync(self, data: Tuple[float, float, float, float, int]) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(
        self,
        data: Union[
            optical_flow_grpc, Tuple[float, float, float, float, int], dict
        ],
    ) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC optical flow object, a tuple of
            (flow_x, flow_y, body_x, body_y, quality), or a JSON dictionary
        """
        if isinstance(data, optical_flow_grpc):
            # Update from gRPC object
            try:
                # Try to copy the whole message
                self.grpc.CopyFrom(data)
            except (AttributeError, TypeError):
                # Fallback to individual field copying
                self.grpc.quality = data.quality

                if hasattr(data, "flow_rate"):
                    self.grpc.flow_rate.x = data.flow_rate.x
                    self.grpc.flow_rate.y = data.flow_rate.y

                if hasattr(data, "body_rate"):
                    self.grpc.body_rate.x = data.body_rate.x
                    self.grpc.body_rate.y = data.body_rate.y

            # Update JSON
            self.json["flow"]["x"] = data.flow_rate.x
            self.json["flow"]["y"] = data.flow_rate.y
            self.json["body"]["x"] = data.body_rate.x
            self.json["body"]["y"] = data.body_rate.y
            self.json["quality"] = data.quality

        elif isinstance(data, tuple) and len(data) == 5:
            # Update from tuple (flow_x, flow_y, body_x, body_y, quality)
            (
                self.grpc.flow_rate.x,
                self.grpc.flow_rate.y,
                self.grpc.body_rate.x,
                self.grpc.body_rate.y,
                self.grpc.quality,
            ) = data

            # Update JSON
            (
                self.json["flow"]["x"],
                self.json["flow"]["y"],
                self.json["body"]["x"],
                self.json["body"]["y"],
                self.json["quality"],
            ) = data

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json = data

            # Update gRPC (using correct nested JSON structure)
            self.grpc.flow_rate.x = data.get("flow", {}).get("x", 0.0)
            self.grpc.flow_rate.y = data.get("flow", {}).get("y", 0.0)
            self.grpc.body_rate.x = data.get("body", {}).get("x", 0.0)
            self.grpc.body_rate.y = data.get("body", {}).get("y", 0.0)
            self.grpc.quality = data.get("quality", 0)

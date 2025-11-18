"""Aruco marker data class"""

import time
from dataclasses import dataclass, field
from typing import List, Union, overload

from ara_api._utils.communication import aruco_grpc


@dataclass
class Aruco:
    """Represents a detected Aruco marker"""

    grpc: aruco_grpc = field(default_factory=lambda: aruco_grpc())
    json: dict = field(
        default_factory=lambda: {
            "id": -1,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0},
            # Extended data not in proto but useful for processing
            "corners": [],
            "center": [0.0, 0.0],
            "marker_size": 0.0,
            "dictionary": 0,
            "timestamp": time.time(),
            "confidence": 0.0,
        }
    )

    def __post_init__(self) -> None:
        if self.json["corners"] and not self.json["center"]:
            self.json["center"] = self._calculate_center()

    def _calculate_center(self) -> List[float]:
        """Calculate the center point from corners"""
        if not self.json["corners"] or len(self.json["corners"]) != 4:
            return [0.0, 0.0]

        x = sum(corner[0] for corner in self.json["corners"]) / 4
        y = sum(corner[1] for corner in self.json["corners"]) / 4
        return [x, y]

    def __repr__(self) -> str:
        return f"Aruco(id={self.json['id']}, position={self.json['position']})"

    @overload
    def sync(self, grpc: aruco_grpc) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(self, data: Union[aruco_grpc, dict]) -> None:
        """Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC aruco object or a JSON dictionary
        """
        if isinstance(data, aruco_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            self.json["id"] = data.id
            if hasattr(data, "position"):
                self.json["position"] = {
                    "x": data.position.x,
                    "y": data.position.y,
                    "z": data.position.z,
                }
            if hasattr(data, "orientation"):
                self.json["orientation"] = {
                    "x": data.orientation.x,
                    "y": data.orientation.y,
                    "z": data.orientation.z,
                }

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json.update(data)

            # Update gRPC
            self.grpc.id = self.json["id"]

            # Handle position
            if "position" in self.json:
                self.grpc.position.x = self.json["position"].get("x", 0.0)
                self.grpc.position.y = self.json["position"].get("y", 0.0)
                self.grpc.position.z = self.json["position"].get("z", 0.0)

            # Handle orientation
            if "orientation" in self.json:
                self.grpc.orientation.x = self.json["orientation"].get(
                    "x", 0.0
                )
                self.grpc.orientation.y = self.json["orientation"].get(
                    "y", 0.0
                )
                self.grpc.orientation.z = self.json["orientation"].get(
                    "z", 0.0
                )

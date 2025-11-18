"""Blob data class"""

import time
from dataclasses import dataclass, field
from typing import List, Union, overload

from ara_api._utils.communication import blob_grpc


@dataclass
class Blob:
    """Represents a detected blob in an image"""

    grpc: blob_grpc = field(default_factory=lambda: blob_grpc())
    json: dict = field(
        default_factory=lambda: {
            "id": -1,
            "position": {"x": 0.0, "y": 0.0},
            "size": 0.0,
            # Extended data not in proto but useful for processing
            "type": 0,
            "contour": [],
            "center": [0.0, 0.0],
            "bounding_box": [0, 0, 0, 0],
            "color": [0, 0, 0],
            "timestamp": time.time(),
            "confidence": 0.0,
        }
    )

    def __post_init__(self) -> None:
        if self.json["contour"] and not self.json["center"]:
            self.json["center"] = self._calculate_center()

        # Size in proto could correspond to area in the extended data
        if self.json["contour"] and self.json["size"] == 0.0:
            area = self._calculate_area()
            self.json["size"] = area

    def _calculate_center(self) -> List[float]:
        """Calculate the center point from the contour"""
        if not self.json["contour"]:
            return [0.0, 0.0]

        x = sum(point[0] for point in self.json["contour"]) / len(
            self.json["contour"]
        )
        y = sum(point[1] for point in self.json["contour"]) / len(
            self.json["contour"]
        )
        return [x, y]

    def _calculate_area(self) -> float:
        """Calculate the area of the contour"""
        if not self.json["contour"] or len(self.json["contour"]) < 3:
            return 0.0

        # Simple polygon area calculation using the Shoelace formula
        area = 0.0
        for i in range(len(self.json["contour"])):
            j = (i + 1) % len(self.json["contour"])
            area += self.json["contour"][i][0] * self.json["contour"][j][1]
            area -= self.json["contour"][j][0] * self.json["contour"][i][1]
        return abs(area) / 2.0

    def __repr__(self) -> str:
        return (
            f"Blob(id={self.json['id']}, position={self.json['position']}, "
            f"size={self.json['size']:.2f})"
        )

    @overload
    def sync(self, grpc: blob_grpc) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(self, data: Union[blob_grpc, dict]) -> None:
        """Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC blob object or a JSON dictionary
        """
        if isinstance(data, blob_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            self.json["id"] = data.id
            if hasattr(data, "position"):
                self.json["position"] = {
                    "x": data.position.x,
                    "y": data.position.y,
                }
            self.json["size"] = data.size

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json.update(data)

            # Update gRPC
            self.grpc.id = self.json.get("id", -1)

            # Handle position
            if "position" in self.json:
                self.grpc.position.x = self.json["position"].get("x", 0.0)
                self.grpc.position.y = self.json["position"].get("y", 0.0)

            # Size/area conversion
            self.grpc.size = self.json.get("size", 0.0)

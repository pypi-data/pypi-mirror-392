"""Image data class"""

import time
from dataclasses import dataclass, field
from typing import Tuple, Union, overload

import numpy as np

from ara_api._utils.communication import image_grpc


@dataclass
class Image:
    """Represents an image with data and metadata"""

    grpc: image_grpc = field(default_factory=lambda: image_grpc())
    json: dict = field(
        default_factory=lambda: {
            "width": 0,
            "height": 0,
            "noise": 0.0,
            "timestamp": 0.0,  # Will be set in __post_init__ or sync
        }
    )
    data: np.ndarray = field(default_factory=lambda: np.array([]))

    def __post_init__(self) -> None:
        if self.data.size > 0:
            self.json["height"], self.json["width"] = self.data.shape[:2]
            self._update_grpc_from_data()
        # Set timestamp if not already set
        if self.json["timestamp"] == 0.0:
            self.json["timestamp"] = time.time()

    def __repr__(self) -> str:
        return (
            f"Image(width={self.json['width']}, height={self.json['height']})"
        )

    def _update_grpc_from_data(self) -> None:
        """Update gRPC message with current image data"""
        self.grpc.height = self.json["height"]
        self.grpc.weight = self.json[
            "width"
        ]  # Note: using 'weight' as per proto definition (likely a typo)
        self.grpc.noise = self.json.get("noise", 0.0)
        if self.data.size > 0:
            self.grpc.data = self.data.tobytes()

    @overload
    def sync(self, grpc: image_grpc) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    @overload
    def sync(self, data: np.ndarray) -> None: ...

    def sync(self, data: Union[image_grpc, dict, np.ndarray]) -> None:
        """Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC image object, a JSON dictionary, or
                  a numpy array
        """
        if isinstance(data, image_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            self.json["height"] = data.height
            self.json["width"] = (
                data.weight
            )  # Note: using 'weight' as per proto definition
            self.json["noise"] = data.noise

            # Update numpy data if gRPC contains image bytes
            if data.data:
                # Validate buffer size and determine format
                total_pixels = data.height * data.weight
                actual_size = len(data.data)

                # Expected sizes for different formats
                expected_sizes = {
                    'grayscale': total_pixels,
                    'bgr': total_pixels * 3,
                    'rgba': total_pixels * 4
                }

                # Determine format based on actual data size
                if actual_size == expected_sizes['grayscale']:
                    shape = (data.height, data.weight)
                elif actual_size == expected_sizes['bgr']:
                    shape = (data.height, data.weight, 3)
                elif actual_size == expected_sizes['rgba']:
                    shape = (data.height, data.weight, 4)
                else:
                    raise ValueError(
                        f"Image data size mismatch: expected one of "
                        f"{list(expected_sizes.values())}, got {actual_size} bytes "
                        f"for dimensions {data.height}x{data.weight}"
                    )

                self.data = np.frombuffer(
                    data.data, dtype=np.uint8
                ).reshape(shape)

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json.update(data)
            self._update_grpc_from_data()

        elif isinstance(data, np.ndarray):
            # Update from numpy array
            self.data = data

            # Update JSON
            self.json["height"], self.json["width"] = data.shape[:2]
            self.json["timestamp"] = time.time()

            # Update gRPC
            self._update_grpc_from_data()

    @property
    def shape(self) -> Tuple:
        """Return image shape"""
        return (
            self.data.shape
            if self.data.size > 0
            else (self.json["height"], self.json["width"])
        )

    @property
    def is_empty(self) -> bool:
        """Check if image data is empty"""
        return self.data.size == 0

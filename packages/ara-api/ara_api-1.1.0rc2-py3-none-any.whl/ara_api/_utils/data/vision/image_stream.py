"""Image stream data class"""

import time
from dataclasses import dataclass, field
from typing import Union

import numpy as np

from ara_api._utils.communication import image_stream_grpc


@dataclass
class ImageStream:
    """Represents a stream of images"""

    grpc: image_stream_grpc = field(
        default_factory=lambda: image_stream_grpc()
    )
    json: dict = field(
        default_factory=lambda: {"timestamp": time.time(), "frame_id": 0}
    )
    data: np.ndarray = field(default_factory=lambda: np.array([]))

    def __repr__(self) -> str:
        data_size = (
            len(self.grpc.data) if hasattr(self.grpc, 'data') else 0
        )
        return (
            f"ImageStream(frame_id={self.json['frame_id']},"
            f" data_size={data_size})"
        )

    def sync(self, data: Union[image_stream_grpc, np.ndarray]) -> None:
        """Update both gRPC and data representations

        Args:
            data: Either a gRPC image_stream object or a numpy array
        """
        if isinstance(data, image_stream_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update frame information
            self.json["frame_id"] = self.json.get("frame_id", 0) + 1
            self.json["timestamp"] = time.time()

            # Update numpy data if possible
            if data.data:
                try:
                    # We don't know the shape from the stream data
                    # The caller will need to reshape it appropriately
                    self.data = np.frombuffer(data.data, dtype=np.uint8)
                except Exception as e:
                    print(f"Error converting stream data: {e}")

        elif isinstance(data, np.ndarray):
            # Update from numpy array
            self.data = data

            # Update JSON
            self.json["frame_id"] = self.json.get("frame_id", 0) + 1
            self.json["timestamp"] = time.time()

            # Update gRPC
            self.grpc.data = data.tobytes()

    def next_frame(self, data: np.ndarray) -> None:
        """Add next frame to the stream"""
        self.sync(data)

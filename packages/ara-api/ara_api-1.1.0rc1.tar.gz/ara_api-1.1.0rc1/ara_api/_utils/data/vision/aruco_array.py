"""Aruco array data class"""

from dataclasses import dataclass, field
from typing import List

from ara_api._utils.communication import aruco_array_grpc
from ara_api._utils.data.vision.aruco import Aruco


@dataclass
class ArucoArray:
    """Array of Aruco markers with gRPC support"""

    grpc: aruco_array_grpc = field(default_factory=lambda: aruco_array_grpc())
    markers: List[Aruco] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure markers list and gRPC are in sync
        # If markers were provided, sync them to gRPC
        # Otherwise, sync from gRPC to markers
        if self.markers:
            self._sync_grpc_from_markers()
        else:
            self._sync_markers_from_grpc()

    def _sync_markers_from_grpc(self) -> None:
        """Update markers list from gRPC data"""
        self.markers = []
        if hasattr(self.grpc, "markers"):
            for aruco_grpc_obj in self.grpc.markers:
                aruco = Aruco()
                aruco.sync(aruco_grpc_obj)
                self.markers.append(aruco)

    def _sync_grpc_from_markers(self) -> None:
        """Update gRPC from markers list"""
        if hasattr(self.grpc, "markers"):
            del self.grpc.markers[:]  # Clear existing markers
            for aruco in self.markers:
                self.grpc.markers.append(aruco.grpc)

    def add(self, marker: Aruco) -> None:
        """Add a marker to the array"""
        self.markers.append(marker)
        if hasattr(self.grpc, "markers"):
            self.grpc.markers.append(marker.grpc)

    def clear(self) -> None:
        """Clear all markers"""
        self.markers.clear()
        if hasattr(self.grpc, "markers"):
            del self.grpc.markers[:]

    def __len__(self) -> int:
        return len(self.markers)

    def __getitem__(self, idx: int) -> Aruco:
        return self.markers[idx]

    def __iter__(self):
        return iter(self.markers)

    def sync(self, data: aruco_array_grpc) -> None:
        """Sync with gRPC aruco array message"""
        self.grpc.CopyFrom(data)
        self._sync_markers_from_grpc()

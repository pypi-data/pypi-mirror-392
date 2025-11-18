"""Blob array data class"""

from dataclasses import dataclass, field
from typing import List

from ara_api._utils.communication import blob_array_grpc
from ara_api._utils.data.vision.blob import Blob


@dataclass
class BlobArray:
    """Array of blobs with gRPC support"""

    grpc: blob_array_grpc = field(default_factory=lambda: blob_array_grpc())
    blobs: List[Blob] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure blobs list and gRPC are in sync
        # If blobs were provided, sync them to gRPC
        # Otherwise, sync from gRPC to blobs
        if self.blobs:
            self._sync_grpc_from_blobs()
        else:
            self._sync_blobs_from_grpc()

    def _sync_blobs_from_grpc(self) -> None:
        """Update blobs list from gRPC data"""
        self.blobs = []
        if hasattr(self.grpc, "blobs"):
            for blob_grpc_obj in self.grpc.blobs:
                blob = Blob()
                blob.sync(blob_grpc_obj)
                self.blobs.append(blob)

    def _sync_grpc_from_blobs(self) -> None:
        """Update gRPC from blobs list"""
        if hasattr(self.grpc, "blobs"):
            del self.grpc.blobs[:]  # Clear existing blobs
            for blob in self.blobs:
                self.grpc.blobs.append(blob.grpc)

    def add(self, blob: Blob) -> None:
        """Add a blob to the array"""
        self.blobs.append(blob)
        if hasattr(self.grpc, "blobs"):
            self.grpc.blobs.append(blob.grpc)

    def clear(self) -> None:
        """Clear all blobs"""
        self.blobs.clear()
        if hasattr(self.grpc, "blobs"):
            del self.grpc.blobs[:]

    def __len__(self) -> int:
        return len(self.blobs)

    def __getitem__(self, idx: int) -> Blob:
        return self.blobs[idx]

    def __iter__(self):
        return iter(self.blobs)

    def sync(self, data: blob_array_grpc) -> None:
        """Sync with gRPC blob array message"""
        self.grpc.CopyFrom(data)
        self._sync_blobs_from_grpc()

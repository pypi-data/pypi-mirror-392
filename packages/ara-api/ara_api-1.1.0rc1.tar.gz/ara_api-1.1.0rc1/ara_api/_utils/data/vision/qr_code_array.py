"""QR code array data class"""

from dataclasses import dataclass, field
from typing import List

from ara_api._utils.communication import qr_array_grpc
from ara_api._utils.data.vision.qr_code import QRCode


@dataclass
class QRCodeArray:
    """Array of QR codes with gRPC support"""

    grpc: qr_array_grpc = field(default_factory=lambda: qr_array_grpc())
    codes: List[QRCode] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure codes list and gRPC are in sync
        # If codes were provided, sync them to gRPC
        # Otherwise, sync from gRPC to codes
        if self.codes:
            self._sync_grpc_from_codes()
        else:
            self._sync_codes_from_grpc()

    def _sync_codes_from_grpc(self) -> None:
        """Update codes list from gRPC data"""
        self.codes = []
        if hasattr(self.grpc, "codes"):
            for qr_grpc_obj in self.grpc.codes:
                qr_code = QRCode()
                qr_code.sync(qr_grpc_obj)
                self.codes.append(qr_code)

    def _sync_grpc_from_codes(self) -> None:
        """Update gRPC from codes list"""
        if hasattr(self.grpc, "codes"):
            del self.grpc.codes[:]  # Clear existing codes
            for qr_code in self.codes:
                self.grpc.codes.append(qr_code.grpc)

    def add(self, code: QRCode) -> None:
        """Add a QR code to the array"""
        self.codes.append(code)
        if hasattr(self.grpc, "codes"):
            self.grpc.codes.append(code.grpc)

    def clear(self) -> None:
        """Clear all QR codes"""
        self.codes.clear()
        if hasattr(self.grpc, "codes"):
            del self.grpc.codes[:]

    def __len__(self) -> int:
        return len(self.codes)

    def __getitem__(self, idx: int) -> QRCode:
        return self.codes[idx]

    def __iter__(self):
        return iter(self.codes)

    def sync(self, data: qr_array_grpc) -> None:
        """Sync with gRPC QR code array message"""
        self.grpc.CopyFrom(data)
        self._sync_codes_from_grpc()

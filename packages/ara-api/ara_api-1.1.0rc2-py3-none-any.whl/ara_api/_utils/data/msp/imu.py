"""IMU data class for Inertial Measurement Unit"""

from dataclasses import dataclass, field
from typing import Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    imu_data as imu_grpc,
)


@dataclass
class IMU:
    grpc: imu_grpc = field(default_factory=lambda: imu_grpc())
    json: dict = field(
        default_factory=lambda: {
            "gyro": {"x": 0.0, "y": 0.0, "z": 0.0},
            "acc": {"x": 0.0, "y": 0.0, "z": 0.0},
            "mag": {"x": 0.0, "y": 0.0, "z": 0.0},
        }
    )

    def __repr__(self):
        return "IMU(gyro={x}, acc={y}, mag={z})".format(
            x=self.grpc.gyro.x, y=self.grpc.gyro.y, z=self.grpc.gyro.z
        )

    @overload
    def sync(self, grpc: imu_grpc) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(
        self,
        data: Union[imu_grpc, dict],
    ) -> None:
        """
        Update both gRPC and JSON representations with new values
        from gRPC and Tuple

        Args:
            data: Either a gRPC imu object or a JSON dictionary
        """
        if isinstance(data, imu_grpc):
            # Updating from gRPC data
            self.grpc.CopyFrom(data)

            # Update JSON representation
            self.json["gyro"]["x"] = data.gyro.x
            self.json["gyro"]["y"] = data.gyro.y
            self.json["gyro"]["z"] = data.gyro.z

            self.json["acc"]["x"] = data.acc.x
            self.json["acc"]["y"] = data.acc.y
            self.json["acc"]["z"] = data.acc.z

            self.json["mag"]["x"] = data.mag.x
            self.json["mag"]["y"] = data.mag.y
            self.json["mag"]["z"] = data.mag.z

        elif isinstance(data, dict):
            # Updating from JSON data
            self.json = data

            # Update gRPC representation
            if "gyro" in data:
                self.grpc.gyro.x = data["gyro"].get("x", 0.0)
                self.grpc.gyro.y = data["gyro"].get("y", 0.0)
                self.grpc.gyro.z = data["gyro"].get("z", 0.0)

            if "acc" in data:
                self.grpc.acc.x = data["acc"].get("x", 0.0)
                self.grpc.acc.y = data["acc"].get("y", 0.0)
                self.grpc.acc.z = data["acc"].get("z", 0.0)

            if "mag" in data:
                self.grpc.mag.x = data["mag"].get("x", 0.0)
                self.grpc.mag.y = data["mag"].get("y", 0.0)
                self.grpc.mag.z = data["mag"].get("z", 0.0)

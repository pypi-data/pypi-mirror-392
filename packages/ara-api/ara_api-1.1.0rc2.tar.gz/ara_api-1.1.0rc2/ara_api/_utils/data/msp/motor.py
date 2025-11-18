"""Motor data class"""

from dataclasses import dataclass, field
from typing import Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    motor_data as motor_grpc,
)


@dataclass
class Motor:
    grpc: motor_grpc = field(default_factory=lambda: motor_grpc())
    json: dict = field(default_factory=lambda: {"motor": [0, 0, 0, 0]})

    def __repr__(self):
        return "Motor({first}, {second}, {third}, {fourth})".format(
            first=self.grpc.data[0],
            second=self.grpc.data[1],
            third=self.grpc.data[2],
            fourth=self.grpc.data[3],
        )

    @overload
    def sync(self, grpc: motor_grpc) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(self, data: Union[motor_grpc, dict]) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC motor object or a JSON dictionary
        """
        if isinstance(data, motor_grpc):
            # Updating from gRPC data
            self.grpc.CopyFrom(data)

            # Update JSON representation
            motor_values = [
                data.data[0],
                data.data[1],
                data.data[2],
                data.data[3],
            ]
            self.json["motor"] = motor_values

        elif isinstance(data, dict):
            # Updating from JSON data
            self.json = data

            # Update gRPC representation
            if "motor" in data and len(data["motor"]) >= 4:
                self.grpc.data = data["motor"]

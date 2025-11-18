"""Drone state data class"""

import time
from dataclasses import dataclass, field
from typing import Tuple, Union

from ara_api._utils.data.nav.path import Path
from ara_api._utils.data.nav.rotation import Rotation
from ara_api._utils.data.nav.vector3 import Vector3
from ara_api._utils.enums import NavigationState


@dataclass
class DroneState:
    ID: int = 0  # for identity of drone
    IP: str = ""  # ip address of drone with {id}
    PORT: str = ""

    position: Vector3 = field(default_factory=lambda: Vector3())
    velocity: Vector3 = field(default_factory=lambda: Vector3())
    attitude: Rotation = field(default_factory=lambda: Rotation([0, 0, 0]))
    timestamp: float = field(default_factory=lambda: time.time())
    battery_voltage: float = 0.0

    state: NavigationState = NavigationState.IDLE
    current_path: Path = field(default_factory=lambda: Path())

    def __post_init__(self) -> None:
        if not isinstance(self.position, Vector3):
            if self.position is not None and isinstance(self.position, tuple):
                self.position = Vector3(
                    x=self.position[0], y=self.position[1], z=self.position[2]
                )
            else:
                raise Exception("Invalid position data")

        if not isinstance(self.attitude, Rotation):
            if self.attitude is not None and isinstance(self.attitude, tuple):
                self.attitude = Rotation(self.attitude)
            else:
                raise Exception("Invalid attitude data")

    def __repr__(self):
        return (
            "DroneState INFO for logs:\n"
            "\tID: {ID}\n"
            "\tIP: {IP}\n"
            "\tPORT: {PORT}\n"
            "\tPosition: {position}\n"
            "\tAttitude: {attitude}\n"
            "\tTimestamp: {timestamp}\n"
            "\tBattery Voltage: {battery_voltage}"
        ).format(
            ID=self.ID,
            IP=self.IP,
            PORT=self.PORT,
            position=self.position,
            attitude=self.attitude,
            timestamp=self.timestamp,
            battery_voltage=self.battery_voltage,
        )

    def transform(
        self,
        rotation: Union[
            Rotation,
            Tuple[float, float, float],
            Tuple[float, float, float, float],
            Tuple[int, int, int],
        ] = None,
        position: Union[Vector3, Tuple[float, float, float]] = None,
    ):
        if rotation is not None:
            self._transform_attitude(rotation)

        if position is not None:
            self._transform_position(position)

    def _transform_position(self, position):
        raise NotImplementedError("Position transformation is not implemented")

    def _transform_attitude(self, rotation):
        raise NotImplementedError("Rotation transformation is not implemented")

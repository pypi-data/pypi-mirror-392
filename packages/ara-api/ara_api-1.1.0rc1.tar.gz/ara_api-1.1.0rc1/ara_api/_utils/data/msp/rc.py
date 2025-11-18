"""RC (Radio Control) input data class"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union, overload

from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    rc_in as rc_in_grpc,
)

if TYPE_CHECKING:
    from ara_api._utils.data.nav.mppi_state import MPPIState

from ara_api._utils.data.msp.rc_config import RCConfig


@dataclass
class RC:
    grpc: rc_in_grpc = field(
        default_factory=lambda: rc_in_grpc(
            ail=1500, # roll
            ele=1500, # pitch
            thr=1000, # throttle
            rud=1500, # yaw
            aux1=2000,
            aux2=1500,
            aux3=1000,
            aux4=1000,
        )
    )
    json: dict = field(
        default_factory=lambda: {
            "rc": [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
        }
    )

    def __repr__(self):
        return (
            "RC(roll={roll}, pitch={pitch}, throttle={throttle}, yaw={yaw}, "
            "aux1={aux1}, aux2={aux2}, aux3={aux3}, aux4={aux4})".format(
                roll=self.grpc.ail,
                pitch=self.grpc.ele,
                throttle=self.grpc.thr,
                yaw=self.grpc.rud,
                aux1=self.grpc.aux1,
                aux2=self.grpc.aux2,
                aux3=self.grpc.aux3,
                aux4=self.grpc.aux4,
            )
        )

    @overload
    def sync(self, grpc: rc_in_grpc) -> None: ...

    @overload
    def sync(self, json: dict) -> None: ...

    def sync(self, data: Union[rc_in_grpc, dict]) -> None:
        """
        Update both gRPC and JSON representations with new values

        Args:
            data: Either a gRPC rc_in object or a JSON dictionary
        """
        if isinstance(data, rc_in_grpc):
            # Update from gRPC object
            self.grpc.CopyFrom(data)

            # Update JSON
            rc_values = [
                data.ail,
                data.ele,
                data.thr,
                data.rud,
                data.aux1,
                data.aux2,
                data.aux3,
                data.aux4,
            ]
            self.json["rc"] = rc_values

        elif isinstance(data, dict):
            # Update from JSON dict
            self.json = data

            # Update gRPC (using correct field names: ail, ele, thr, rud)
            if "rc" in data and len(data["rc"]) >= 8:
                self.grpc.ail = data["rc"][0]  # aileron (roll)
                self.grpc.ele = data["rc"][1]  # elevator (pitch)
                self.grpc.thr = data["rc"][2]  # throttle
                self.grpc.rud = data["rc"][3]  # rudder (yaw)
                self.grpc.aux1 = data["rc"][4]
                self.grpc.aux2 = data["rc"][5]
                self.grpc.aux3 = data["rc"][6]
                self.grpc.aux4 = data["rc"][7]

    def transform_from_vel(
        self,
        x: float,
        y: float,
        z: float,
        w: float,
        state: Optional["MPPIState"] = None,
        dt: float = 0.1,
    ) -> None:
        pitch_rc = self._map(
            x,
            -RCConfig.MAX_PITCH_VEL,
            RCConfig.MAX_PITCH_VEL,
            RCConfig.MIN_CHANNEL_INPUT,
            RCConfig.MAX_CHANNEL_INPUT,
        )

        roll_rc = self._map(
            y,
            -RCConfig.MAX_ROLL_VEL,
            RCConfig.MAX_ROLL_VEL,
            RCConfig.MIN_CHANNEL_INPUT,
            RCConfig.MAX_CHANNEL_INPUT,
        )

        yaw_rc = self._map(
            w,
            -RCConfig.MAX_YAW_VEL,
            RCConfig.MAX_YAW_VEL,
            RCConfig.MIN_CHANNEL_INPUT,
            RCConfig.MAX_CHANNEL_INPUT,
        )

        if state is not None:
            target_z = state.position.z + z * dt
        else:
            target_z = 0

        throttle_rc = self._map(
            target_z,
            -RCConfig.MAX_THROTTLE,
            RCConfig.MAX_THROTTLE,
            RCConfig.MIN_CHANNEL_INPUT,
            RCConfig.MAX_CHANNEL_INPUT,
        )

        self.sync(
            {
                "rc": [
                    pitch_rc,
                    roll_rc,
                    throttle_rc,
                    yaw_rc,
                    self.grpc.aux1,
                    self.grpc.aux2,
                    self.grpc.aux3,
                    self.grpc.aux4,
                ]
            }
        )

    def _map(
        self,
        value: float,
        from_min: float,
        from_max: float,
        to_min: int,
        to_max: int,
    ) -> float:
        """
        Map a value from one range to another with linear interpolation.
        """
        value = max(from_min, min(from_max, value))  # Clamp value

        from_span = from_max - from_min
        to_span = to_max - to_min

        value_scaled = (value - from_min) / from_span

        final_value = to_min + (value_scaled * to_span)

        return int(final_value)

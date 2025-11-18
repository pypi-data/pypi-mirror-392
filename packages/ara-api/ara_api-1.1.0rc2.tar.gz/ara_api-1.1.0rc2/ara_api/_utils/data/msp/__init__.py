"""
MSP data classes for sensors and rc_in with support of returning grpc
values and converting for sending with websocket
"""

from ara_api._utils.data.msp.altitude import Altitude
from ara_api._utils.data.msp.analog import Analog
from ara_api._utils.data.msp.attitude import Attitude
from ara_api._utils.data.msp.imu import IMU
from ara_api._utils.data.msp.motor import Motor
from ara_api._utils.data.msp.optical_flow import OpticalFlow
from ara_api._utils.data.msp.position import Position
from ara_api._utils.data.msp.rc import RC
from ara_api._utils.data.msp.rc_config import RCConfig
from ara_api._utils.data.msp.sonar import Sonar
from ara_api._utils.data.msp.velocity import Velocity

__all__ = [
    "RCConfig",
    "IMU",
    "Motor",
    "Position",
    "Velocity",
    "Attitude",
    "OpticalFlow",
    "Altitude",
    "Sonar",
    "Analog",
    "RC",
]

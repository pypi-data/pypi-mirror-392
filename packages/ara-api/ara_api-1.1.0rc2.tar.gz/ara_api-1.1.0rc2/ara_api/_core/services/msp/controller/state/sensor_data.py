"""Sensor Data State

This module contains dataclasses for sensor readings.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class OdometryData:
    """Odometry data from position estimator"""

    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    yaw: List[float] = field(default_factory=lambda: [0.0])


@dataclass
class SensorData:
    """Sensor readings from flight controller

    Contains IMU, altitude, sonar, optical flow and odometry data.
    """

    gyroscope: List[int] = field(default_factory=lambda: [0, 0, 0])
    accelerometer: List[int] = field(default_factory=lambda: [0, 0, 0])
    magnetometer: List[int] = field(default_factory=lambda: [0, 0, 0])
    altitude: float = 0.0
    sonar: float = 0.0
    kinematics: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    debug: List[int] = field(
        default_factory=lambda: [0, 0, 0, 0, 0, 0, 0, 0]
    )
    odom: OdometryData = field(default_factory=OdometryData)
    optical_flow: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility"""
        return {
            "gyroscope": self.gyroscope,
            "accelerometer": self.accelerometer,
            "magnetometer": self.magnetometer,
            "altitude": self.altitude,
            "sonar": self.sonar,
            "kinematics": self.kinematics,
            "debug": self.debug,
            "odom": {
                "position": self.odom.position,
                "velocity": self.odom.velocity,
                "yaw": self.odom.yaw,
            },
            "optical_flow": self.optical_flow,
        }

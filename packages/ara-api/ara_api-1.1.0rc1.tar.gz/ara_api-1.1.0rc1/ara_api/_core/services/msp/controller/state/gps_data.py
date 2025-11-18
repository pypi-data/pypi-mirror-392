"""GPS Data State

This module contains the dataclass for GPS information.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class GPSData:
    """GPS data from flight controller

    Contains position, satellite info, and navigation data.
    """

    fix: int = 0
    num_sat: int = 0
    lat: float = 0.0
    lon: float = 0.0
    alt: float = 0.0
    speed: float = 0.0
    ground_course: float = 0.0
    distance_to_home: float = 0.0
    direction_to_home: float = 0.0
    update: int = 0
    chn: List[int] = field(default_factory=list)
    svid: List[int] = field(default_factory=list)
    quality: List[int] = field(default_factory=list)
    cno: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility"""
        return {
            "fix": self.fix,
            "numSat": self.num_sat,
            "lat": self.lat,
            "lon": self.lon,
            "alt": self.alt,
            "speed": self.speed,
            "ground_course": self.ground_course,
            "distanceToHome": self.distance_to_home,
            "ditectionToHome": self.direction_to_home,
            "update": self.update,
            "chn": self.chn,
            "svid": self.svid,
            "quality": self.quality,
            "cno": self.cno,
        }

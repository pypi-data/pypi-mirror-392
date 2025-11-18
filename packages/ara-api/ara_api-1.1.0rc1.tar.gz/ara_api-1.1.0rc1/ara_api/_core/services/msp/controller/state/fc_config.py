"""Flight Controller Configuration State

This module contains the dataclass for flight controller configuration.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class FCConfig:
    """Flight Controller Configuration

    Stores all configuration parameters received from the flight controller.
    """

    api_version: str = "0.0.0"
    flight_controller_identifier: str = ""
    flight_controller_version: str = ""
    version: int = 0
    build_info: str = ""
    multi_type: int = 0
    msp_version: int = 0
    capability: int = 0
    cycle_time: int = 0
    i2c_error: int = 0
    active_sensors: int = 0
    mode: int = 0
    profile: int = 0
    uid: List[int] = field(default_factory=lambda: [0, 0, 0])
    accelerometer_trims: List[int] = field(default_factory=lambda: [0, 0])
    name: str = ""
    display_name: str = "JOE PILOT"
    num_profiles: int = 3
    rate_profile: int = 0
    board_type: int = 0
    arming_disable_count: int = 0
    arming_disable_flags: int = 0
    arming_disabled: bool = False
    runaway_takeoff_prevention_disabled: bool = False
    board_identifier: str = ""
    board_version: int = 0
    comm_capabilities: int = 0
    target_name: str = ""
    board_name: str = ""
    manufacturer_id: str = ""
    signature: List[int] = field(default_factory=list)
    mcu_type_id: int = 255

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility.

        Returns snake_case keys converted to camelCase.
        """
        return {
            "apiVersion": self.api_version,
            "flightControllerIdentifier": self.flight_controller_identifier,
            "flightControllerVersion": self.flight_controller_version,
            "version": self.version,
            "buildInfo": self.build_info,
            "multiType": self.multi_type,
            "msp_version": self.msp_version,
            "capability": self.capability,
            "cycleTime": self.cycle_time,
            "i2cError": self.i2c_error,
            "activeSensors": self.active_sensors,
            "mode": self.mode,
            "profile": self.profile,
            "uid": self.uid,
            "accelerometerTrims": self.accelerometer_trims,
            "name": self.name,
            "displayName": self.display_name,
            "numProfiles": self.num_profiles,
            "rateProfile": self.rate_profile,
            "boardType": self.board_type,
            "armingDisableCount": self.arming_disable_count,
            "armingDisableFlags": self.arming_disable_flags,
            "armingDisabled": self.arming_disabled,
            "runawayTakeoffPreventionDisabled": (
                self.runaway_takeoff_prevention_disabled
            ),
            "boardIdentifier": self.board_identifier,
            "boardVersion": self.board_version,
            "commCapabilities": self.comm_capabilities,
            "targetName": self.target_name,
            "boardName": self.board_name,
            "manufacturerId": self.manufacturer_id,
            "signature": self.signature,
            "mcuTypeId": self.mcu_type_id,
        }

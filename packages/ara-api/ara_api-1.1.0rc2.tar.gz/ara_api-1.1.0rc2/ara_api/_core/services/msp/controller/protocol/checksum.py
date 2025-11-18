"""MSP Protocol Checksum Functions

This module provides checksum calculation functions for MSP V1 (XOR)
and MSP V2 (CRC8-DVB-S2).
"""

from typing import Union

from ara_api._core.services.msp.controller.protocol.constants import (
    CRC8_DVB_S2_POLY,
)


def calculate_xor_checksum(data: Union[bytearray, bytes]) -> int:
    """Calculate XOR checksum for MSP V1 protocol.

    Args:
        data: Bytes to calculate checksum for

    Returns:
        XOR checksum value (0-255)
    """
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum


def calculate_crc8_dvb_s2(
    data: Union[bytearray, bytes], initial: int = 0
) -> int:
    """Calculate CRC8-DVB-S2 checksum for MSP V2 protocol.

    Uses polynomial 0xD5 for CRC calculation.

    Args:
        data: Bytes to calculate checksum for
        initial: Initial CRC value (default: 0)

    Returns:
        CRC8 checksum value (0-255)
    """
    crc = initial
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) & 0xFF) ^ CRC8_DVB_S2_POLY
            else:
                crc = (crc << 1) & 0xFF
    return crc


def verify_xor_checksum(
    data: Union[bytearray, bytes], expected: int
) -> bool:
    """Verify XOR checksum for MSP V1 protocol.

    Args:
        data: Bytes to verify
        expected: Expected checksum value

    Returns:
        True if checksum matches, False otherwise
    """
    return calculate_xor_checksum(data) == expected


def verify_crc8_checksum(
    data: Union[bytearray, bytes], expected: int, initial: int = 0
) -> bool:
    """Verify CRC8-DVB-S2 checksum for MSP V2 protocol.

    Args:
        data: Bytes to verify
        expected: Expected checksum value
        initial: Initial CRC value (default: 0)

    Returns:
        True if checksum matches, False otherwise
    """
    return calculate_crc8_dvb_s2(data, initial) == expected

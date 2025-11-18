"""MSP Protocol Constants

This module contains all magic numbers, protocol constants,
and MSP codes used in the MultiWii Serial Protocol V1 and V2.
"""

from typing import Final

# Protocol magic bytes
MAGIC_DOLLAR: Final[int] = 36  # $
MAGIC_M: Final[int] = 77  # M (MSP V1)
MAGIC_X: Final[int] = 88  # X (MSP V2)
MAGIC_LT: Final[int] = 60  # < (PC to FC)
MAGIC_GT: Final[int] = 62  # > (FC to PC)
MAGIC_EXCL: Final[int] = 33  # ! (Error/Unsupported)

# Protocol versions
MSP_V1: Final[int] = 1
MSP_V2: Final[int] = 2

# Frame sizes
MSP_V1_OVERHEAD: Final[int] = 6  # $ + M + < + len + code + checksum
MSP_V2_OVERHEAD: Final[int] = 9  # $ + X + < + flag + code + len + crc
JUMBO_FRAME_SIZE_LIMIT: Final[int] = 255

# Message directions
DIRECTION_PC_TO_FC: Final[int] = 0
DIRECTION_FC_TO_PC: Final[int] = 1

# CRC polynomial for MSP V2
CRC8_DVB_S2_POLY: Final[int] = 0xD5

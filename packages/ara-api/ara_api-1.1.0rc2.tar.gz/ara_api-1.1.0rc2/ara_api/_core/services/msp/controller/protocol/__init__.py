"""MSP Protocol Layer

This module provides encoding and decoding functionality for the
MultiWii Serial Protocol (MSP) V1 and V2.
"""

from ara_api._core.services.msp.controller.protocol.checksum import (
    calculate_crc8_dvb_s2,
    calculate_xor_checksum,
    verify_crc8_checksum,
    verify_xor_checksum,
)
from ara_api._core.services.msp.controller.protocol.constants import (
    CRC8_DVB_S2_POLY,
    DIRECTION_FC_TO_PC,
    DIRECTION_PC_TO_FC,
    JUMBO_FRAME_SIZE_LIMIT,
    MAGIC_DOLLAR,
    MAGIC_EXCL,
    MAGIC_GT,
    MAGIC_LT,
    MAGIC_M,
    MAGIC_X,
    MSP_V1,
    MSP_V1_OVERHEAD,
    MSP_V2,
    MSP_V2_OVERHEAD,
)
from ara_api._core.services.msp.controller.protocol.decoder import (
    DecoderState,
    MSPDecoder,
    MSPMessage,
)
from ara_api._core.services.msp.controller.protocol.encoder import MSPEncoder

__all__ = [
    # Encoder/Decoder
    "MSPEncoder",
    "MSPDecoder",
    "MSPMessage",
    "DecoderState",
    # Checksum functions
    "calculate_xor_checksum",
    "calculate_crc8_dvb_s2",
    "verify_xor_checksum",
    "verify_crc8_checksum",
    # Constants
    "MSP_V1",
    "MSP_V2",
    "MSP_V1_OVERHEAD",
    "MSP_V2_OVERHEAD",
    "MAGIC_DOLLAR",
    "MAGIC_M",
    "MAGIC_X",
    "MAGIC_LT",
    "MAGIC_GT",
    "MAGIC_EXCL",
    "DIRECTION_PC_TO_FC",
    "DIRECTION_FC_TO_PC",
    "JUMBO_FRAME_SIZE_LIMIT",
    "CRC8_DVB_S2_POLY",
]

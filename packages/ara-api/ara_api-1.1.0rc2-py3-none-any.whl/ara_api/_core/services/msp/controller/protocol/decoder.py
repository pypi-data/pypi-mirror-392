"""MSP Protocol Decoder

This module provides decoding functionality for MSP V1 and V2.
Implements a state machine for incremental message parsing with
optimized buffer management.
"""

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional

from ara_api._core.services.msp.controller.protocol.checksum import (
    verify_crc8_checksum,
)
from ara_api._core.services.msp.controller.protocol.constants import (
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
    MSP_V2,
)


class DecoderState(Enum):
    """MSP Decoder State Machine States"""

    IDLE = auto()
    SYNC_CHAR_1 = auto()
    SYNC_CHAR_2 = auto()
    DIRECTION = auto()
    V2_FLAG = auto()
    V2_CODE_LOW = auto()
    V2_CODE_HIGH = auto()
    V1_LEN = auto()
    V2_LEN_LOW = auto()
    V2_LEN_HIGH = auto()
    V1_CODE = auto()
    JUMBO_FRAME_LEN_LOW = auto()
    JUMBO_FRAME_LEN_HIGH = auto()
    PAYLOAD_SETUP = auto()
    PAYLOAD = auto()
    CHECKSUM = auto()
    ERROR = auto()


@dataclass
class MSPMessage:
    """Decoded MSP message"""

    code: int = 0
    data: bytearray = field(default_factory=bytearray)
    msp_version: int = MSP_V1
    direction: int = DIRECTION_FC_TO_PC
    timestamp: float = field(default_factory=time.time)
    crc_error: bool = False
    packet_error: bool = False
    unsupported: bool = False

    def reset(self) -> None:
        """Reset message to initial state for reuse"""
        self.code = 0
        self.data = bytearray()
        self.msp_version = MSP_V1
        self.direction = DIRECTION_FC_TO_PC
        self.timestamp = time.time()
        self.crc_error = False
        self.packet_error = False
        self.unsupported = False


class MSPDecoder:
    """Optimized MSP protocol decoder for V1 and V2.

    Implements a state machine for incremental parsing of MSP messages.
    Reuses buffers to minimize allocations in hot paths.
    """

    def __init__(self) -> None:
        # State machine
        self._state = DecoderState.IDLE
        self._msp_version = MSP_V1

        # Message being built
        self._code = 0
        self._direction = DIRECTION_FC_TO_PC
        self._expected_len = 0
        self._received_len = 0
        self._is_jumbo_frame = False

        # Pre-allocated buffer for payload (reused)
        self._max_buffer_size = 2048
        self._buffer = bytearray(self._max_buffer_size)

        # Checksum tracking
        self._checksum = 0

        # Flags
        self._unsupported = False
        self._crc_error = False
        self._packet_error = False

        # Timestamp
        self._timestamp = time.time()

        # Reusable message object
        self._message = MSPMessage()

    def reset(self) -> None:
        """Reset decoder to initial state"""
        self._state = DecoderState.IDLE
        self._msp_version = MSP_V1
        self._code = 0
        self._direction = DIRECTION_FC_TO_PC
        self._expected_len = 0
        self._received_len = 0
        self._is_jumbo_frame = False
        self._checksum = 0
        self._unsupported = False
        self._crc_error = False
        self._packet_error = False

    def decode_byte(self, byte: int) -> Optional[MSPMessage]:
        """Process single byte through state machine.

        Args:
            byte: Byte to process (0-255)

        Returns:
            Complete MSPMessage if message fully decoded, None otherwise
        """
        if self._state == DecoderState.IDLE:
            if byte == MAGIC_DOLLAR:  # $
                self._timestamp = time.time()
                self._state = DecoderState.SYNC_CHAR_1
                return None

        elif self._state == DecoderState.SYNC_CHAR_1:
            if byte == MAGIC_M:  # M - MSP V1
                self._msp_version = MSP_V1
                self._state = DecoderState.SYNC_CHAR_2
            elif byte == MAGIC_X:  # X - MSP V2
                self._msp_version = MSP_V2
                self._state = DecoderState.SYNC_CHAR_2
            else:
                self._packet_error = True
                return self._error_message()

        elif self._state == DecoderState.SYNC_CHAR_2:
            if byte == MAGIC_EXCL:  # ! - Unsupported
                self._unsupported = True
                return self._error_message()
            elif byte == MAGIC_GT:  # > - FC to PC
                self._direction = DIRECTION_FC_TO_PC
            elif byte == MAGIC_LT:  # < - PC to FC
                self._direction = DIRECTION_PC_TO_FC
            else:
                self._packet_error = True
                return self._error_message()

            # Branch based on version
            if self._msp_version == MSP_V1:
                self._state = DecoderState.V1_LEN
            else:
                self._state = DecoderState.V2_FLAG

        elif self._state == DecoderState.V2_FLAG:
            # MSP V2: Flag byte (currently ignored, reserved)
            self._state = DecoderState.V2_CODE_LOW

        elif self._state == DecoderState.V2_CODE_LOW:
            # MSP V2: Code low byte
            self._code = byte
            self._state = DecoderState.V2_CODE_HIGH

        elif self._state == DecoderState.V2_CODE_HIGH:
            # MSP V2: Code high byte
            self._code |= byte << 8
            self._state = DecoderState.V2_LEN_LOW

        elif self._state == DecoderState.V1_LEN:
            # MSP V1: Length byte
            self._expected_len = byte
            self._checksum = byte  # Start XOR checksum

            if byte == JUMBO_FRAME_SIZE_LIMIT:
                self._is_jumbo_frame = True
                self._state = DecoderState.V1_CODE
            else:
                self._state = DecoderState.V1_CODE

        elif self._state == DecoderState.V2_LEN_LOW:
            # MSP V2: Length low byte
            self._expected_len = byte
            self._state = DecoderState.V2_LEN_HIGH

        elif self._state == DecoderState.V2_LEN_HIGH:
            # MSP V2: Length high byte
            self._expected_len |= byte << 8

            # Allocate buffer if needed
            if self._expected_len > len(self._buffer):
                self._buffer = bytearray(self._expected_len)

            if self._expected_len > 0:
                self._state = DecoderState.PAYLOAD_SETUP
            else:
                self._state = DecoderState.CHECKSUM

        elif self._state == DecoderState.V1_CODE:
            # MSP V1: Code byte
            self._code = byte
            self._checksum ^= byte  # Update XOR checksum

            if self._is_jumbo_frame:
                self._state = DecoderState.JUMBO_FRAME_LEN_LOW
            elif self._expected_len > 0:
                # Allocate buffer if needed
                if self._expected_len > len(self._buffer):
                    self._buffer = bytearray(self._expected_len)
                self._state = DecoderState.PAYLOAD_SETUP
            else:
                self._state = DecoderState.CHECKSUM

        elif self._state == DecoderState.JUMBO_FRAME_LEN_LOW:
            # Jumbo frame: Length low byte
            self._expected_len = byte
            self._checksum ^= byte
            self._state = DecoderState.JUMBO_FRAME_LEN_HIGH

        elif self._state == DecoderState.JUMBO_FRAME_LEN_HIGH:
            # Jumbo frame: Length high byte
            self._expected_len += 256 * byte
            self._checksum ^= byte

            # Allocate buffer for jumbo frame
            if self._expected_len > len(self._buffer):
                self._buffer = bytearray(self._expected_len)

            self._state = DecoderState.PAYLOAD_SETUP

        elif self._state == DecoderState.PAYLOAD_SETUP:
            # First payload byte
            self._buffer[0] = byte
            self._received_len = 1

            if self._msp_version == MSP_V1:
                self._checksum ^= byte

            if self._received_len >= self._expected_len:
                self._state = DecoderState.CHECKSUM
            else:
                self._state = DecoderState.PAYLOAD

        elif self._state == DecoderState.PAYLOAD:
            # Payload bytes
            self._buffer[self._received_len] = byte
            self._received_len += 1

            if self._msp_version == MSP_V1:
                self._checksum ^= byte

            if self._received_len >= self._expected_len:
                self._state = DecoderState.CHECKSUM

        elif self._state == DecoderState.CHECKSUM:
            # Verify checksum and return message
            if self._msp_version == MSP_V1:
                if self._checksum == byte:
                    return self._success_message()
                else:
                    self._crc_error = True
                    return self._error_message()
            else:
                # MSP V2: Calculate CRC8
                crc_data = bytearray(
                    [
                        0,  # flag
                        self._code & 0xFF,
                        (self._code >> 8) & 0xFF,
                        self._expected_len & 0xFF,
                        (self._expected_len >> 8) & 0xFF,
                    ]
                )
                crc_data.extend(self._buffer[: self._received_len])

                if verify_crc8_checksum(crc_data, byte):
                    return self._success_message()
                else:
                    self._crc_error = True
                    return self._error_message()

        return None

    def decode_bytes(
        self,
        data: bytes,
        callback: Optional[Callable[[MSPMessage], None]] = None,
    ) -> Optional[MSPMessage]:
        """Decode multiple bytes, returning first complete message.

        Args:
            data: Bytes to decode
            callback: Optional callback for each complete message

        Returns:
            First complete message, or None if no complete message yet
        """
        for byte in data:
            msg = self.decode_byte(byte)
            if msg:
                if callback:
                    callback(msg)
                return msg
        return None

    def _success_message(self) -> MSPMessage:
        """Build successful message and reset decoder"""
        # Reuse message object
        self._message.reset()
        self._message.code = self._code
        self._message.data = bytearray(
            self._buffer[: self._received_len]
        )  # Copy
        self._message.msp_version = self._msp_version
        self._message.direction = self._direction
        self._message.timestamp = self._timestamp
        self._message.crc_error = False
        self._message.packet_error = False
        self._message.unsupported = False

        # Reset for next message
        self.reset()

        return self._message

    def _error_message(self) -> MSPMessage:
        """Build error message and reset decoder"""
        self._message.reset()
        self._message.code = self._code
        self._message.crc_error = self._crc_error
        self._message.packet_error = self._packet_error
        self._message.unsupported = self._unsupported
        self._message.timestamp = self._timestamp

        # Reset for next message
        self.reset()

        return self._message

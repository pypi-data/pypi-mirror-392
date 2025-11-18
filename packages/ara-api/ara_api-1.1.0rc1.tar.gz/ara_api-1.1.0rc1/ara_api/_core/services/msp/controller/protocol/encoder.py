"""MSP Protocol Encoder

This module provides encoding functionality for MSP V1 and V2 protocols.
Optimized for performance with buffer reuse and minimal allocations.
"""

from typing import List, Union

from ara_api._core.services.msp.controller.protocol.checksum import (
    calculate_crc8_dvb_s2,
    calculate_xor_checksum,
)
from ara_api._core.services.msp.controller.protocol.constants import (
    MAGIC_DOLLAR,
    MAGIC_LT,
    MAGIC_M,
    MAGIC_X,
    MSP_V1,
    MSP_V1_OVERHEAD,
    MSP_V2,
    MSP_V2_OVERHEAD,
)


class MSPEncoder:
    """Optimized MSP protocol encoder for V1 and V2.

    Pre-allocates buffers for common message sizes to reduce
    allocations in hot paths. Supports both MSP V1 (XOR checksum)
    and MSP V2 (CRC8 checksum).
    """

    # Pre-allocate buffers for common sizes (most msgs < 64 bytes)
    BUFFER_POOL_SIZES = [32, 64, 128, 256, 512]

    def __init__(self) -> None:
        # Pre-allocate buffer pool for common sizes
        self._buffer_pool = {
            size: bytearray(size) for size in self.BUFFER_POOL_SIZES
        }
        # For sizes not in pool, allocate on demand
        self._max_pool_size = max(self.BUFFER_POOL_SIZES)

    def encode_v1(
        self, code: int, data: Union[List[int], bytearray, bytes] = b""
    ) -> bytearray:
        """Encode MSP V1 message.

        Format: $ + M + < + len + code + data + checksum(XOR)

        Args:
            code: MSP command code (0-254)
            data: Payload data

        Returns:
            Encoded message as bytearray
        """
        data_len = len(data)
        total_size = data_len + MSP_V1_OVERHEAD

        # Get buffer from pool or allocate new one
        if total_size in self._buffer_pool:
            buffer = self._buffer_pool[total_size]
        elif total_size <= self._max_pool_size:
            # Find next larger buffer in pool
            buffer = next(
                (
                    self._buffer_pool[size]
                    for size in self.BUFFER_POOL_SIZES
                    if size >= total_size
                ),
                bytearray(total_size),
            )
        else:
            buffer = bytearray(total_size)

        # Build message
        buffer[0] = MAGIC_DOLLAR  # $
        buffer[1] = MAGIC_M  # M
        buffer[2] = MAGIC_LT  # <
        buffer[3] = data_len
        buffer[4] = code

        # Copy payload
        if data_len > 0:
            buffer[5 : 5 + data_len] = data

        # Calculate XOR checksum over len + code + data
        checksum_data = buffer[3 : 5 + data_len]
        buffer[5 + data_len] = calculate_xor_checksum(checksum_data)

        # Return only the used portion if from pool
        if total_size <= self._max_pool_size:
            return bytearray(buffer[:total_size])
        return buffer

    def encode_v2(
        self, code: int, data: Union[List[int], bytearray, bytes] = b""
    ) -> bytearray:
        """Encode MSP V2 message.

        Format: $ + X + < + flag + code_low + code_high + len_low +
                len_high + data + checksum(CRC8)

        Args:
            code: MSP command code (256-65535)
            data: Payload data

        Returns:
            Encoded message as bytearray
        """
        data_len = len(data)
        total_size = data_len + MSP_V2_OVERHEAD

        # Get buffer from pool or allocate new one
        if total_size in self._buffer_pool:
            buffer = self._buffer_pool[total_size]
        elif total_size <= self._max_pool_size:
            # Find next larger buffer in pool
            buffer = next(
                (
                    self._buffer_pool[size]
                    for size in self.BUFFER_POOL_SIZES
                    if size >= total_size
                ),
                bytearray(total_size),
            )
        else:
            buffer = bytearray(total_size)

        # Build message
        buffer[0] = MAGIC_DOLLAR  # $
        buffer[1] = MAGIC_X  # X
        buffer[2] = MAGIC_LT  # <
        buffer[3] = 0  # flag (reserved)
        buffer[4] = code & 0xFF  # code low byte
        buffer[5] = (code >> 8) & 0xFF  # code high byte
        buffer[6] = data_len & 0xFF  # len low byte
        buffer[7] = (data_len >> 8) & 0xFF  # len high byte

        # Copy payload
        if data_len > 0:
            buffer[8 : 8 + data_len] = data

        # Calculate CRC8 checksum over flag + code + len + data
        checksum_data = buffer[3 : 8 + data_len]
        buffer[8 + data_len] = calculate_crc8_dvb_s2(checksum_data)

        # Return only the used portion if from pool
        if total_size <= self._max_pool_size:
            return bytearray(buffer[:total_size])
        return buffer

    def encode(
        self,
        code: int,
        data: Union[List[int], bytearray, bytes] = b"",
        version: int = MSP_V1,
    ) -> bytearray:
        """Encode MSP message with automatic version selection.

        Args:
            code: MSP command code
            data: Payload data
            version: Protocol version (MSP_V1 or MSP_V2)

        Returns:
            Encoded message as bytearray

        Raises:
            ValueError: If version is invalid
        """
        if version == MSP_V1:
            if code >= 255:
                raise ValueError(
                    f"MSP V1 requires code < 255, got {code}. "
                    "Use MSP V2 for codes >= 255."
                )
            return self.encode_v1(code, data)
        elif version == MSP_V2:
            if code < 256:
                raise ValueError(
                    f"MSP V2 requires code >= 256, got {code}. "
                    "Use MSP V1 for codes < 255."
                )
            return self.encode_v2(code, data)
        else:
            raise ValueError(
                f"Invalid MSP version: {version}. "
                f"Must be {MSP_V1} or {MSP_V2}."
            )

    def encode_auto(
        self, code: int, data: Union[List[int], bytearray, bytes] = b""
    ) -> bytearray:
        """Encode MSP message with automatic version detection.

        Automatically selects MSP V1 for code < 255,
        MSP V2 for code >= 256.

        Args:
            code: MSP command code
            data: Payload data

        Returns:
            Encoded message as bytearray
        """
        if code < 255:
            return self.encode_v1(code, data)
        else:
            return self.encode_v2(code, data)

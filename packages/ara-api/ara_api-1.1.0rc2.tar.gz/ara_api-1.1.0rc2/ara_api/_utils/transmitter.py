"""
Transmitter module for handling various communication protocols.

This module provides classes for network and serial communication,
implementing the base Transmitter interface. It supports TCP socket
connections and serial port communications with configurable parameters
such as connection timeouts, buffer sizes, and error handling.

Classes:
    TCPTransmitter: Handles TCP socket-based communications
    SerialTransmitter: Handles serial port communications

    Each transmitter implementation provides methods for connecting,
    disconnecting, sending and receiving data according to the specific
    protocol requirements.
"""

import errno  # Added for socket error codes
import select  # Added for select-based send
import socket
import time  # Add for time-based calculations
from threading import Lock
from typing import Optional, Union

import serial  # Added for SerialTransmitter

from ara_api._utils.interfaces import Transmitter
from ara_api._utils.logger import Logger


# TODO: добавить возможность настройки логирования через аргументы
class TCPTransmitter(Transmitter):
    """
    Transmitter module for handling various communication protocols.

    This module provides classes for network and serial communication,
    implementing the base Transmitter interface. It supports TCP socket
    connections and serial port communications with configurable
    parameters such as connection timeouts, buffer sizes,
    and error handling.

    Classes:
        TCPTransmitter: Handles TCP socket-based communications
        SerialTransmitter: Handles serial port communications

    Each transmitter implementation provides methods for connecting,
    disconnecting, sending and receiving data according to the specific
    protocol requirements.
    """

    def __init__(self, address, log: bool = False, output: bool = False):
        """
        Initialize a new TCP transmitter instance.

        Args:
            address (tuple): A tuple containing (host, port) for
                             the TCP connection
        """
        super().__init__()
        self.logger = Logger(log_to_file=log, log_to_terminal=output)
        self.logger.info(f"Initializing TCPTransmitter on {address}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.buffersize = 0  # Will be updated after connection

        # Initialize to disconnected state (follows base class contract)
        self.closed = True
        self.timeout_exception = socket.timeout
        self.host = address[0]
        self.port = address[1]
        self.timeout = None
        self.write_lock = Lock()  # Add a lock for thread-safe send operations

    def connect(self, timeout: float = 2.0):
        """
        Establish a connection to the configured TCP socket.

        Attempts to connect to the host and port specified during
        initialization.

        Args:
            timeout (float, optional): Connection timeout in seconds.
                                       Defaults to 2.0.

        Returns:
            bool: True if connection was successful, False otherwise

        Raises:
            ConnectionError: If the connection attempt fails
        """
        self.logger.info(
            f"Connecting to {self.host}:{self.port} with timeout {timeout}"
        )
        try:
            # Set timeout before attempting connection to prevent
            # indefinite blocking
            self.sock.settimeout(timeout)
            self.sock.connect((self.host, self.port))
            # Reset to blocking mode after successful connection
            self.sock.settimeout(None)
            self.logger.debug(
                "Socket reset to blocking mode after successful connection."
            )
            self.closed = False
            # Get the actual buffer size after the connection
            # is established
            self.buffersize = self.sock.getsockopt(
                socket.SOL_SOCKET, socket.SO_RCVBUF
            )
            self.logger.info(
                f"Socket receive buffer size set to {self.buffersize} bytes."
            )
            self.timeout = timeout  # Store the actual timeout used
            self.logger.info(
                f"Successfully connected to {self.host}:{self.port}"
            )
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            self.closed = True
            raise

        return (
            not self.closed
        )  # Return True if connected (not closed), False otherwise

    def disconnect(self):
        """
        Close the current TCP socket connection.

        Safely closes the connection and updates the internal state.
        """
        self.logger.info(
            f"Disconnecting from {self.host}:{self.port} (current state: "
            f"{'closed' if self.closed else 'open'})"
        )
        if not self.closed and self.sock:
            try:
                # Gracefully shut down read/write operations.
                # This can help notify the peer.
                self.sock.shutdown(socket.SHUT_RDWR)
                self.logger.debug("Socket shutdown successful.")
            except OSError as e:
                if e.errno not in (
                    errno.ENOTCONN,
                    errno.EBADF,
                    errno.ECONNRESET,
                ):
                    self.logger.warning(
                        f"Error during socket shutdown: {e} (errno {e.errno})"
                    )
                else:
                    self.logger.debug(
                        f"Socket shutdown benign error "
                        f"(already closed/reset): {e}"
                    )
            finally:
                # Always attempt to close the socket descriptor
                try:
                    self.sock.close()
                    self.logger.info("Socket closed successfully.")
                except OSError as e_close:
                    # EBADF if already closed, which is fine here.
                    if e_close.errno != errno.EBADF:
                        self.logger.warning(
                            f"Error during socket close: {e_close} "
                            f"(errno {e_close.errno})"
                        )
                    else:
                        self.logger.debug(
                            f"Socket close benign error (already closed): "
                            f"{e_close}"
                        )
        elif self.closed:
            self.logger.info("Socket already marked as closed.")
        elif not self.sock:
            self.logger.info(
                "Socket object does not exist, nothing to disconnect."
            )

        self.closed = True

    def reconnect(self, attempts: int = 3, delay: float = 1.0) -> bool:
        """
        Attempt to reconnect to the TCP socket.

        Args:
            attempts (int): Number of reconnection attempts.
            delay (float): Delay between attempts in seconds.

        Returns:
            bool: True if reconnection was successful, False otherwise.
        """
        self.logger.info(f"Attempting to reconnect to {self.host}:{self.port}")
        self.disconnect()

        for attempt in range(attempts):
            try:
                self.logger.info(
                    f"Reconnection attempt {attempt + 1}/{attempts}"
                )
                # Create a new socket instance for reconnection
                # This replaces the old self.sock object
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                connect_timeout = (
                    self.timeout if self.timeout is not None else 2.0
                )
                self.logger.debug(
                    f"Using connect timeout: {connect_timeout}s "
                    f"for reconnect attempt {attempt + 1}"
                )
                self.sock.settimeout(connect_timeout)

                self.sock.connect((self.host, self.port))
                self.closed = False  # Mark as open

                # Update buffersize for the new socket
                try:
                    self.buffersize = self.sock.getsockopt(
                        socket.SOL_SOCKET, socket.SO_RCVBUF
                    )
                    self.logger.info(
                        f"Socket receive buffer size updated to "
                        f"{self.buffersize} bytes after reconnect."
                    )
                except socket.error as e_sockopt:
                    self.logger.warning(
                        f"Could not get SO_RCVBUF after reconnect: "
                        f"{e_sockopt}. Using previous: {self.buffersize}"
                    )

                if self.timeout is not None:
                    self.sock.settimeout(self.timeout)
                    self.logger.debug(
                        f"Restored operational timeout to {self.timeout}s"
                        f" on reconnected socket."
                    )
                else:
                    self.sock.settimeout(None)
                    self.logger.debug(
                        "Reconnected socket set to blocking mode "
                        "(default operational timeout)."
                    )

                self.logger.info(
                    f"Successfully reconnected to {self.host}:{self.port}"
                )
                return True  # Reconnection successful

            except socket.timeout as e_timeout:
                self.logger.warning(
                    f"Reconnection attempt {attempt + 1} timed out: {e_timeout}"
                )
                # Close the failed socket before retrying or
                # failing permanently
                if self.sock:
                    try:
                        self.sock.close()
                    except OSError:
                        pass  # Ignore errors if socket is already closed
                self.closed = (
                    True  # Ensure state is closed after a failed attempt
                )

            except socket.error as e_sock:
                self.logger.warning(
                    f"Reconnection attempt {attempt + 1} "
                    f"failed with socket error: {e_sock}"
                )
                if self.sock:  # Ensure socket is closed if it was created
                    try:
                        self.sock.close()
                    except OSError:
                        pass  # Ignore errors if socket is already closed
                self.closed = True  # Ensure state is closed

            # If this attempt failed and more attempts are left, delay
            if attempt < attempts - 1:
                self.logger.info(
                    f"Waiting {delay}s before next reconnection attempt."
                )
                time.sleep(delay)
            else:
                self.logger.error("All reconnection attempts failed.")
                # self.closed is already True from the last failed
                # attempt's except block
                raise ConnectionError(
                    f"Failed to reconnect to {self.host}:{self.port} "
                    f"after {attempts} attempts."
                )

        return (
            False  # Should only be reached if attempts is 0 (or logic error)
        )

    def _send_with_select(
        self,
        sock_to_use: socket.socket,
        data_view: memoryview,
        operation_timeout: float,
    ) -> int:
        """
        Internal helper to send data using select for non-blocking I/O
        and timeout management.

        Args:
            sock_to_use: The socket object to use for sending.
            data_view: A memoryview of the data to send.
            operation_timeout: Timeout for the send operation in seconds
                               - > 0: Specific timeout.
                               - == 0: Non-blocking (poll).
                               - == -1: Block indefinitely until all
                                        data sent or error.

        Returns:
            Number of bytes sent.

        Raises:
            socket.timeout: If the operation times out.
            ConnectionError: If a connection or socket error occurs.
        """
        original_sock_timeout_setting = sock_to_use.gettimeout()
        made_sock_non_blocking = False

        try:
            if (
                original_sock_timeout_setting != 0
            ):  # If not already non-blocking
                sock_to_use.setblocking(False)
                made_sock_non_blocking = True

            bytes_sent = 0
            total_bytes = len(data_view)
            deadline = -1.0

            if operation_timeout > 0:
                deadline = time.monotonic() + operation_timeout

            while bytes_sent < total_bytes:
                current_select_timeout = (
                    -1.0
                )  # Default for operation_timeout == -1 (block indefinitely)

                if deadline > 0:  # Specific timeout for operation
                    remaining_time = deadline - time.monotonic()
                    if remaining_time <= 0:
                        self.logger.warning(
                            f"Send operation timed out before select for "
                            f"remaining {total_bytes - bytes_sent} bytes."
                        )
                        raise socket.timeout(
                            "Send operation timed out (deadline reached)"
                        )
                    current_select_timeout = remaining_time
                elif (
                    operation_timeout == 0
                ):  # Non-blocking send attempt (poll)
                    current_select_timeout = 0.0

                # self.logger.debug(f"select() with timeout:
                # {current_select_timeout}")
                try:
                    # Corrected unpacking: select returns (readable,
                    # writable, exceptional)
                    # We are interested in the writable list for sending
                    readable_sockets, ready_to_write, exceptional_sockets = (
                        select.select(
                            [],
                            [sock_to_use],
                            [sock_to_use],
                            current_select_timeout
                            if current_select_timeout >= 0
                            else None,
                        )
                    )
                except select.error as e:
                    self.logger.error(f"select.error during send: {e}")
                    self.closed = True
                    raise ConnectionError(
                        f"select.error during send: {e}"
                    ) from e
                except (
                    ValueError
                ) as e:  # Can happen if socket is closed then used in select
                    self.logger.error(
                        f"ValueError during select (socket likely closed): {e}"
                    )
                    self.closed = True
                    raise ConnectionError(
                        f"ValueError during select (socket closed): {e}"
                    ) from e

                if exceptional_sockets:
                    err = 0
                    try:
                        err = sock_to_use.getsockopt(
                            socket.SOL_SOCKET, socket.SO_ERROR
                        )
                    except socket.error as sock_opt_err:
                        self.logger.error(
                            f"Failed to get SO_ERROR: {sock_opt_err}"
                        )
                        self.closed = True
                        raise ConnectionError(
                            f"Socket exception during send "
                            f"(getsockopt failed: {sock_opt_err})"
                        )

                    error_code = errno.errorcode.get(err, str(err))
                    self.logger.error(
                        f"Socket in exceptional state during send select "
                        f"(SO_ERROR={err}, errno={error_code})."
                    )
                    self.closed = True
                    raise ConnectionError(
                        f"Socket exception during send (SO_ERROR={err}, "
                        f"errno={errno.errorcode.get(err, str(err))})"
                    )

                if not ready_to_write:
                    if operation_timeout == 0:
                        self.logger.warning(
                            "Send operation would block "
                            "(select not writable with timeout=0)."
                        )
                        raise socket.timeout(
                            "Send operation would block (non-blocking)"
                        )
                    else:  # select timed out
                        self.logger.warning(
                            f"Send operation timed out during select, "
                            f"{bytes_sent}/{total_bytes} sent."
                        )
                        raise socket.timeout(
                            "Send operation timed out (select)"
                        )

                # Socket is writable
                try:
                    sent_this_call = sock_to_use.send(data_view[bytes_sent:])
                    if sent_this_call == 0:
                        self.logger.error(
                            "Socket connection broken (send returned 0 bytes)."
                        )
                        self.closed = True
                        raise ConnectionError(
                            "Socket connection broken (send returned 0 bytes)"
                        )
                    bytes_sent += sent_this_call
                    # self.logger.debug(f"Sent {sent_this_call} bytes in
                    # this call, total {bytes_sent}/{total_bytes}")
                except socket.error as e:
                    if e.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                        if (
                            operation_timeout == 0
                        ):  # Polling, and it would block
                            self.logger.warning(
                                "Send operation would block (EWOULDBLOCK "
                                "with timeout=0)."
                            )
                            raise socket.timeout(
                                "Send operation would block (EWOULDBLOCK)"
                            )
                        # self.logger.debug(f"Send would block
                        # (EWOULDBLOCK/EAGAIN),
                        # {bytes_sent}/{total_bytes} sent.
                        # Retrying with select.")
                        continue  # Loop back to select
                    else:
                        self.logger.error(
                            f"Socket error during non-blocking send: {e}"
                        )
                        self.closed = True
                        raise ConnectionError(
                            f"Socket error during send: {e}"
                        ) from e

            return bytes_sent

        finally:
            if made_sock_non_blocking:
                try:
                    if original_sock_timeout_setting is None:
                        sock_to_use.setblocking(True)
                    else:
                        sock_to_use.settimeout(original_sock_timeout_setting)
                    # self.logger.debug(f"Restored socket blocking
                    # state to: {original_sock_timeout_setting}")
                except socket.error as e_restore:
                    self.logger.warning(
                        f"Could not restore socket blocking state: {e_restore}"
                    )

    def send(
        self,
        bufView: Union[bytes, bytearray, memoryview],
        blocking: bool = True,
        timeout: int = -1,
    ):
        """
        Send data over the established TCP connection using select-based non-blocking I/O.
        This method is thread-safe.

        Args:
            bufView (Union[bytes, bytearray, memoryview]): Binary data to be transmitted.
            blocking (bool, optional): If True (default), block until all data is sent or timeout.
                                      If False, perform a non-blocking send (timeout is effectively 0).
            timeout (int, optional): Write timeout in seconds.
                                   - If > 0, specific timeout for the operation.
                                   - If == 0, non-blocking attempt.
                                   - If == -1 (default), block indefinitely (respects socket's default if applicable,
                                     but for select this means block in select until ready).

        Returns:
            int: Number of bytes successfully sent.

        Raises:
            ConnectionError: If the connection is closed or sending/reconnection fails.
            ValueError: If the data is not in a valid binary format (though memoryview handles this).
            socket.timeout: If the send operation times out.
        """
        effective_timeout = float(
            timeout
        )  # Ensure float for time calculations
        if not blocking:
            if timeout != -1 and timeout != 0:
                self.logger.warning(
                    f"send called with blocking=False and timeout={timeout}. "
                    "Forcing non-blocking behavior (timeout=0)."
                )
            effective_timeout = 0.0

        with self.write_lock:
            if not bufView:
                self.logger.warning(
                    "Empty data buffer provided to send method"
                )
                return 0

            self.logger.debug(
                f"Attempting to send {len(bufView)} bytes. Blocking: {blocking}, Timeout: {timeout}, EffectiveTO: {effective_timeout}"
            )

            if self.closed:
                self.logger.error(
                    "Cannot send data: TCP connection not established"
                )
                raise ConnectionError("Socket is closed, cannot send data")

            if not self.sock:
                self.logger.error("Socket object is not initialized")
                self.closed = (
                    True  # Should already be true if sock is None after init
                )
                raise ConnectionError("Socket object is not available")

            data_to_send = memoryview(bufView)

            try:
                # Initial attempt
                bytes_sent = self._send_with_select(
                    self.sock, data_to_send, effective_timeout
                )
                self.logger.debug(
                    f"Successfully sent {bytes_sent} bytes on initial attempt."
                )
                return bytes_sent

            except (
                socket.timeout,
                ConnectionError,
                BrokenPipeError,
                ConnectionResetError,
                OSError,
            ) as e:
                self.logger.warning(
                    f"Send failed on initial attempt: {str(e)}. Attempting to reconnect."
                )

                # Ensure socket is marked closed before attempting reconnect if error implies it
                if not isinstance(
                    e, socket.timeout
                ):  # Timeouts don't always mean socket is dead
                    self.closed = True

                if (
                    self.reconnect()
                ):  # self.sock is now the new reconnected socket
                    self.logger.info(
                        "Reconnection successful. Retrying send operation."
                    )
                    try:
                        bytes_sent_retry = self._send_with_select(
                            self.sock, data_to_send, effective_timeout
                        )
                        self.logger.debug(
                            f"Successfully sent {bytes_sent_retry} bytes after reconnection."
                        )
                        return bytes_sent_retry
                    except (socket.timeout, ConnectionError) as e2:
                        self.logger.error(
                            f"Send failed after reconnection: {str(e2)}"
                        )
                        self.closed = True
                        raise ConnectionError(
                            f"Send failed after reconnection: {str(e2)}"
                        ) from e2
                    except Exception as e_unexpected_retry:
                        self.logger.error(
                            f"Unexpected error during send retry: {type(e_unexpected_retry).__name__}: {e_unexpected_retry}"
                        )
                        self.closed = True
                        raise ConnectionError(
                            f"Unexpected error during send retry: {e_unexpected_retry}"
                        ) from e_unexpected_retry
                else:  # Reconnect failed
                    self.logger.error(
                        "Failed to reconnect, send operation aborted."
                    )
                    self.closed = True  # Ensure closed state
                    raise ConnectionError(
                        f"Send failed (reconnect also failed): {str(e)}"
                    ) from e

            except Exception as e_unexpected_initial:
                self.logger.error(
                    f"Unexpected error during initial send: {type(e_unexpected_initial).__name__}: {e_unexpected_initial}"
                )
                self.closed = True
                raise ConnectionError(
                    f"Unexpected error during initial send: {e_unexpected_initial}"
                ) from e_unexpected_initial

    def receive(self, size: int, timeout: Optional[float] = None):
        """
        Receive data from the TCP connection.

        Args:
            size (int): Maximum number of bytes to receive. If non-positive, uses default socket buffer size.
            timeout (Optional[float], optional): Read timeout in seconds.
                                                 If provided, temporarily overrides the socket's default timeout.
                                                 If None (default), uses the socket's current timeout setting.

        Returns:
            bytes: Data received from the connection. Can be empty if a timeout occurred before any data.

        Raises:
            ConnectionError: If the connection is closed, if the peer closes the connection gracefully,
                             or if a socket/OS error occurs during receive.
        """
        if self.closed:
            self.logger.error(
                "Cannot receive data: TCP connection not established"
            )
            raise ConnectionError("Socket is closed, cannot receive data")

        if size <= 0:
            self.logger.debug(
                f"Receive called with size <= 0, attempting to receive up to SO_RCVBUF: {self.buffersize} bytes"
            )
            read_size = self.buffersize
            if (
                read_size <= 0
            ):  # Should not happen with standard socket options
                self.logger.warning(
                    f"Default receive buffer size is {read_size}, this might be an issue."
                )
                # Default to a small positive if SO_RCVBUF is problematic, though recv(0) might be fine.
                # However, recv(0) returns b'', which would be misinterpreted as peer close.
                # Let's ensure read_size is positive.
                read_size = 1024 if read_size <= 0 else read_size
        else:
            read_size = size
            self.logger.debug(f"Attempting to receive up to {read_size} bytes")

        recvbuffer = b""
        original_socket_timeout = None
        timeout_was_changed_by_this_method = False

        try:
            # Temporarily set socket timeout if a specific timeout for this operation is provided
            if timeout is not None:
                original_socket_timeout = self.sock.gettimeout()
                # Only change if the requested timeout is different from the current socket timeout
                if original_socket_timeout != timeout:
                    self.sock.settimeout(timeout)
                    timeout_was_changed_by_this_method = True
                    self.logger.debug(
                        f"Temporarily setting socket read timeout to {timeout} seconds for this operation."
                    )

            self.logger.debug(
                f"Calling sock.recv({read_size}) with effective socket timeout: {self.sock.gettimeout()}s"
            )
            recvbuffer = self.sock.recv(read_size)

        except socket.timeout:
            # Timeout occurred during self.sock.recv().
            # recvbuffer may contain partial data if the timeout happened mid-stream, or b'' if immediate.
            self.logger.warning(
                f"Socket timeout during receive operation. Received {len(recvbuffer)} bytes before timeout."
            )
            # Execution will proceed to the finally block, then the return statement at the end.
        except (
            ConnectionError
        ) as e:  # Includes ConnectionResetError, BrokenPipeError etc.
            self.logger.error(f"Connection error during receive: {str(e)}")
            self.closed = True  # Mark connection as closed
            raise  # Re-raise the caught ConnectionError
        except OSError as e:  # Other socket-related OS errors
            self.logger.error(f"OSError during receive: {str(e)}")
            self.closed = True  # Mark connection as closed
            raise ConnectionError(
                f"Socket OSError during receive: {str(e)}"
            ) from e  # Wrap in ConnectionError
        else:
            # This block executes only if no exception occurred in the try block.
            if not recvbuffer:
                # If self.sock.recv() returns an empty byte string without an exception,
                # it signifies that the peer has closed the connection gracefully.
                self.logger.warning(
                    "Socket connection gracefully closed by peer (recv returned empty string)."
                )
                self.closed = True  # Mark connection as closed
                raise ConnectionError("Socket connection closed by peer.")

            self.logger.debug(
                f"Successfully received {len(recvbuffer)} bytes."
            )
        finally:
            # Restore original socket timeout if it was changed by this method call
            if (
                timeout_was_changed_by_this_method
                and original_socket_timeout is not None
            ):
                try:
                    # Check current timeout before restoring, in case socket is already closed or in error state
                    current_sock_timeout = self.sock.gettimeout()
                    if current_sock_timeout != original_socket_timeout:
                        self.sock.settimeout(original_socket_timeout)
                        self.logger.debug(
                            f"Restored socket timeout to {original_socket_timeout} seconds."
                        )
                except OSError as e_restore:  # Socket might be closed or in an invalid state
                    self.logger.warning(
                        f"Could not restore socket timeout post-receive: {str(e_restore)}"
                    )

        return recvbuffer

    def local_read(self, size=1):
        """
        Read data directly from the communication channel with minimal processing.

        This is a low-level method that bypasses most of the error handling and logging
        found in the standard receive method, providing direct access to the raw data stream.

        Args:
            size (int): Number of bytes to read from the channel

        Returns:
            bytes: The raw data read from the communication channel

        Raises:
            ConnectionError: If the connection is closed or reading fails
        """
        self.logger.debug(f"Performing local read of {size} bytes")
        if self.closed:
            self.logger.error(
                "Cannot perform local read: TCP connection not established"
            )
            raise ConnectionError("Socket is closed, cannot read data")

        data = self.sock.recv(size)
        self.logger.debug(f"Local read returned {len(data)} bytes")
        return data


# TODO: добавить возможность настройки логирования через аргументы
class SerialTransmitter(Transmitter):
    """
    Serial port communication implementation of the Transmitter interface.

    This class enables communication over serial ports (RS-232, USB-to-Serial, etc.)
    with configurable parameters such as baud rate, parity, and flow control.
    It provides methods for establishing connections, sending and receiving data,
    and handling serial port errors.

    Attributes:
        logger: Logger instance for recording serial operations and errors
        serial_client: Serial port connection object
        port (str): Serial port device identifier (e.g., '/dev/ttyUSB0', 'COM3')
        baudrate (int): Communication speed in bits per second
        parity: Parity checking type ('N', 'E', 'O', 'M', 'S')
        stopbits (float): Number of stop bits (1, 1.5, 2)
        bytesize (int): Number of data bits (5, 6, 7, 8)
        timeout (float): Read timeout value in seconds
        write_timeout (float): Write timeout value in seconds
        xonxoff (bool): Software flow control flag
        rtscts (bool): Hardware (RTS/CTS) flow control flag
        dsrdtr (bool): Hardware (DSR/DTR) flow control flag
        closed (bool): Flag indicating if the serial connection is closed
        lock (Lock): Threading lock for ensuring thread-safe operations
    """

    def __init__(
        self, port, baud=115200, log: bool = False, output: bool = False
    ):
        """
        Initialize a new SerialTransmitter instance.

        Sets up a serial port connection with the specified parameters but does not
        open the connection. Use the connect() method to establish the connection.

        Args:
            port (str): Serial port identifier (e.g., '/dev/ttyUSB0', 'COM3')
            baud (int, optional): Baud rate for the serial connection. Defaults to 115200.

        Attributes initialized:
            closed (bool): Connection status flag, initially True (disconnected)
            write_lock (Lock): Thread lock for write operations
            read_lock (Lock): Thread lock for read operations
            serial_client (Serial): PySerial object configured with the specified parameters

        Note:
            The serial connection is configured with 8 data bits, no parity,
            and 1 stop bit by default.
        """
        super().__init__()
        self.logger = Logger(log_to_file=log, log_to_terminal=output)
        self.logger.info(
            f"Initializing SerialTransmitter on port {port} at {baud} baud"
        )

        self.write_lock = Lock()
        self.read_lock = Lock()
        self.serial_client = serial.Serial()
        self.serial_client.port = port
        self.serial_client.baudrate = baud
        self.serial_client.bytesize = serial.EIGHTBITS
        self.serial_client.parity = serial.PARITY_NONE
        self.serial_client.stopbits = serial.STOPBITS_ONE
        self.serial_client.timeout = 1
        self.serial_client.xonxoff = False
        self.serial_client.rtscts = False
        self.serial_client.dsrdtr = False
        self.serial_client.write_timeout = 1

    def connect(self):
        """
        Establish a connection to the configured serial port.

        Opens the serial port with the parameters specified during initialization.

        Returns:
            bool: True if connection was successful, False otherwise

        Raises:
            serial.SerialException: If the serial port cannot be opened
        """
        if self.closed:
            try:
                self.logger.info(
                    f"Connecting to serial port {self.serial_client.port}"
                )
                self.serial_client.open()
                self.closed = False
                self.logger.info(
                    f"Successfully connected to serial port {self.serial_client.port}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to connect to serial port {self.serial_client.port}: {str(e)}"
                )
                raise
        else:
            self.logger.info("Serial connection already established")

        return (
            not self.closed
        )  # Return True if connected (not closed), False otherwise

    def disconnect(self):
        """
        Close the current serial port connection.

        Safely closes the connection and updates the internal state.

        Returns:
            bool: True if disconnection was successful, False otherwise
        """
        if not self.closed:
            try:
                self.logger.info(
                    f"Disconnecting from serial port {self.serial_client.port}"
                )
                self.serial_client.close()
                self.closed = True
                self.logger.info(
                    f"Successfully disconnected from serial port {self.serial_client.port}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to close serial port {self.serial_client.port}: {str(e)}"
                )
                raise
        else:
            self.logger.info("Serial connection already closed")

    def send(
        self,
        bufView: Union[bytes, bytearray, memoryview],
        blocking: bool = True,
        timeout: int = -1,
    ):
        """
        Send data over the established serial connection.

        Args:
            bufView (bytes or bytearray): Binary data to be transmitted
            blocking (bool, optional): If True, block until all data is written or timeout occurs. Defaults to True.
            timeout (int, optional): Write timeout in seconds. If -1, use the serial port's default timeout. Defaults to -1.

        Returns:
            int: Number of bytes successfully sent

        Raises:
            ConnectionError: If the connection is closed or sending fails
            ValueError: If the data is not in bytes format
            serial.SerialTimeoutException: If the write times out
        """
        if self.closed:
            self.logger.error(
                "Cannot send data: serial connection not established"
            )
            raise ConnectionError(
                "Serial connection is closed, cannot send data."
            )

        total_sent = 0
        try:
            with self.write_lock:
                buffer_size = len(bufView)
                self.logger.debug(
                    f"Sending {buffer_size} bytes to serial port"
                )

                # Set timeout if specified
                original_timeout = self.serial_client.write_timeout
                if timeout > 0:
                    self.serial_client.write_timeout = timeout

                if blocking:
                    # Keep writing until all data is sent or timeout occurs
                    while total_sent < buffer_size:
                        sent = self.serial_client.write(bufView[total_sent:])
                        if sent == 0 or sent is None:
                            # Break if no data was written or a timeout occurred (returned None)
                            self.logger.debug(
                                f"Write operation returned {sent}, breaking loop"
                            )
                            break
                        total_sent += sent
                else:
                    # Non-blocking mode: Just try once and return how much was sent
                    sent = self.serial_client.write(bufView)
                    # Handle potential None return value on timeout
                    if sent is not None:
                        total_sent = sent

                # Restore original timeout
                if timeout > 0:
                    self.serial_client.write_timeout = original_timeout

                self.logger.debug(
                    f"Successfully sent {total_sent} of {buffer_size} bytes"
                )
        except serial.SerialTimeoutException as e:
            self.logger.warning(
                f"Serial write timed out after sending {total_sent} bytes: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Failed to send data: {str(e)}")
            raise

        return total_sent

    def _blocking_receive(self, size: int) -> bytes:
        """Helper method for blocking serial receive.
        Relies on `self.serial_client.timeout` being appropriately
        set by the caller for the desired timeout behavior of
        `self.serial_client.read()`.
        """
        data = bytearray()
        bytes_remaining = size

        max_iterations = (
            size * 2
        )  # Heuristic: allow at most 2 reads per byte requested
        iterations = 0

        while bytes_remaining > 0 and iterations < max_iterations:
            iterations += 1
            try:
                chunk = self.serial_client.read(bytes_remaining)
            except serial.SerialException as e:
                self.logger.error(f"SerialException during blocking read: {e}")
                break  # Stop on serial error

            if not chunk:
                # This means a timeout occurred as per serial_client.timeout
                self.logger.debug(
                    f"Blocking read: serial_client.read timed out or returned no data. Bytes read: {len(data)}"
                )
                break  # Exit loop on timeout or if no data is read

            data.extend(chunk)
            bytes_remaining -= len(chunk)
            self.logger.debug(
                f"Blocking read: chunk received {len(chunk)} bytes, {bytes_remaining} remaining."
            )

            # If serial_client.timeout is 0 (effectively non-blocking for the read call itself),
            # and we are in this blocking helper, we should break after one attempt if not all data is read.
            # This scenario implies the caller wants to read what's immediately available but in a "blocking" call structure.
            if self.serial_client.timeout == 0 and bytes_remaining > 0:
                self.logger.debug(
                    "Blocking read with serial_client.timeout=0: breaking after first read attempt."
                )
                break

        if iterations >= max_iterations and bytes_remaining > 0:
            self.logger.warning(
                f"Blocking read: Exceeded max iterations ({max_iterations}) before reading all {size} bytes. Read {len(data)} bytes."
            )

        self.logger.debug(
            f"Blocking read: Received {len(data)} of {size} bytes requested."
        )
        return bytes(data)

    def _non_blocking_receive(self, size: int) -> bytes:
        """Helper method for non-blocking serial receive."""
        # For non-blocking, ensure serial_client.timeout is 0 for the read call.
        original_port_timeout = self.serial_client.timeout
        if self.serial_client.timeout != 0:
            self.serial_client.timeout = 0

        try:
            data = self.serial_client.read(size)
        except serial.SerialException as e:
            self.logger.error(f"SerialException during non-blocking read: {e}")
            data = b""  # Return empty on error
        finally:
            # Restore original port timeout if we changed it for this non-blocking call
            if original_port_timeout != 0 and self.serial_client.timeout == 0:
                self.serial_client.timeout = original_port_timeout

        self.logger.debug(f"Non-blocking read: Received {len(data)} bytes.")
        return bytes(data)

    def receive(self, size: int, blocking: bool = True, timeout: int = -1):
        """
        Receive data from the serial connection.

        Args:
            size (int): Maximum number of bytes to receive
            blocking (bool, optional): If True, block until all data is received or timeout occurs.
                                      If False, perform a non-blocking read. Defaults to True.
            timeout (int, optional): Read timeout in seconds.
                                     If -1 (default), uses the serial port's configured `self.serial_client.timeout`.
                                     If 0, implies a non-blocking read attempt for both blocking & non-blocking modes.
                                     If >0, this timeout is used for the read operation.

        Returns:
            bytes: Data received from the connection

        Raises:
            ConnectionError: If the connection is closed or receiving fails
        """
        if self.closed:
            self.logger.error(
                "Cannot receive data: serial connection not established"
            )
            raise ConnectionError("Serial connection not established")

        data = b""
        original_port_timeout = (
            self.serial_client.timeout
        )  # Store the port's default timeout
        effective_timeout_changed = False

        try:
            with self.read_lock:
                # Determine the actual timeout to use for the serial port for this call
                actual_serial_timeout = original_port_timeout
                if timeout != -1:  # User specified a timeout override
                    actual_serial_timeout = timeout
                    if self.serial_client.timeout != actual_serial_timeout:
                        self.serial_client.timeout = actual_serial_timeout
                        effective_timeout_changed = True
                        self.logger.debug(
                            f"Set serial read timeout to {actual_serial_timeout}s for this operation."
                        )

                # If non-blocking mode is requested, ensure timeout is 0 for the read call
                # This overrides any other timeout setting for the duration of the non-blocking call.
                if not blocking:
                    if self.serial_client.timeout != 0:
                        # We will handle this inside _non_blocking_receive to ensure it's always 0 for that path
                        # self.serial_client.timeout = 0
                        # effective_timeout_changed = True # This change is managed by the helper
                        self.logger.debug(
                            "Non-blocking mode requested, will use timeout 0 for read."
                        )
                    # For non-blocking, the `timeout` parameter to this function is less relevant
                    # than ensuring the actual serial port read is non-blocking (timeout=0).

                self.logger.debug(
                    f"Attempting to receive {size} bytes. Blocking: {blocking}, Effective serial_timeout for op: {self.serial_client.timeout}"
                )

                if blocking:
                    # The _blocking_receive helper will use the currently set self.serial_client.timeout
                    data = self._blocking_receive(size)
                else:
                    # _non_blocking_receive ensures its read is with timeout=0
                    data = self._non_blocking_receive(size)

        except serial.SerialException as e:
            self.logger.error(f"SerialException during receive: {str(e)}")
            # Do not re-raise if we want to return partial data or empty; depends on contract.
            # For now, let it fall through to return whatever data was collected (likely empty).
            # Consider re-raising or raising a custom error if this is critical.
        except Exception as e:
            self.logger.error(f"Failed to receive data: {str(e)}")
            raise  # Re-raise other unexpected exceptions
        finally:
            # Restore original port timeout if it was changed for this specific operation
            if effective_timeout_changed:
                try:
                    self.serial_client.timeout = original_port_timeout
                    self.logger.debug(
                        f"Restored serial read timeout to {original_port_timeout}s."
                    )
                except Exception as ex_restore:
                    self.logger.error(
                        f"Failed to restore serial timeout: {ex_restore}"
                    )

        return data  # Ensure return type is bytes, helpers should return bytes

    def local_read(self, size: int):
        """
        Read data directly from the serial port with minimal processing.

        This is a low-level method that bypasses most of the error handling and logging
        found in the standard receive method, providing direct access to the raw data stream.

        Args:
            size (int): Number of bytes to read from the serial port. Defaults to 1.

        Returns:
            bytes: The raw data read from the serial port

        Raises:
            ConnectionError: If the connection is closed or reading fails
        """
        self.logger.debug(f"Performing local read of {size} bytes")

        if self.closed:
            error_msg = (
                "Cannot perform local read: serial connection not established"
            )
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)

        with self.read_lock:
            data = self.serial_client.read(size)
        self.logger.debug(f"Local read returned {len(data)} bytes")
        return data

"""
Core interfaces for the ARA API system architecture.

This module defines the abstract base classes that form the foundation
of the ARA API component hierarchy. These interfaces establish the
contract that concrete implementations must fulfill, ensuring consistent
behavior across the system.

The architecture follows a layered approach:
- Services represent top-level operational units providing
  domain-specific functionality
- Controllers handle specific aspects of system operation and data flow
- Specialized interfaces like Transmitter, DataProcessor, and
  SensorInterface address particular functional domains

Each interface defines the minimum set of methods that implementing
classes must provide, establishing a common vocabulary and interaction
pattern across the codebase.

These interfaces enable loose coupling between components, facilitate
testing through dependency injection, and provide clear documentation
of component responsibilities.
"""

from abc import ABC, abstractmethod


class Service(ABC):
    """
    Base interface for all service components in the ARA API system.

    Services represent top-level operational units that provide specific
    functionality domains such as navigation, vision processing,
    MSP communication, or analysis. Each service encapsulates related
    operations and typically manages one or more controllers.

    Implementing classes should define the 'serve' method to initialize
    and run the service's main functionality loop.
    """

    @abstractmethod
    def serve(self):
        pass


class Controller(ABC):
    """
    Base interface for controller components that handle data
    processing and transmission.

    Controllers are responsible for managing specific aspects of the
    system's operation, such as hardware communication, data
    transformation, or command execution. They typically operate at a
    lower level than Services and focus on specific tasks.

    Implementing classes should define methods to process incoming data
    and send outgoing commands or information to the
    appropriate destination.
    """

    @abstractmethod
    def process_data(self, data):
        pass

    @abstractmethod
    def send_data(self, data):
        pass


class Transmitter(ABC):
    def __init__(self):
        """Initialize the base transmitter state.

        Sets the initial connection state to closed (True).
        All subclasses should call super().__init__() to ensure proper
        initialization.
        """
        self.closed = True

    @abstractmethod
    def connect(self):
        """
        Establish a connection to the configured communication channel.

        This method should handle all the necessary setup to create a
        connection to the specified endpoint, configure any required
        parameters, and update the instance state to reflect
        the connection status.

        Returns:
            bool: True if connection was successful, False otherwise

        Raises:
            ConnectionError: If the connection attempt fails
            TimeoutError: If the connection attempt times out
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Close the current communication channel connection.

        This method should properly close any open connections, release
        resources, and update the instance state to reflect the
        disconnection.

        Returns:
            bool: True if disconnection was successful, False otherwise

        Raises:
            ConnectionError: If the disconnection operation fails
        """
        pass

    @abstractmethod
    def send(self, bufView, blocking=True, timeout=-1):
        """
        Send data over the established communication channel.

        This method transmits binary data over the configured connection

        Args:
            bufView (bytes or bytearray): Binary data to be transmitted
            blocking (bool, optional): If True, block until all data
                                      is written or timeout occurs.
                                      Defaults to True.
            timeout (int, optional): Write timeout in seconds. If -1,
                                     use the channel's default timeout.
                                     Defaults to -1.

        Returns:
            int: Number of bytes successfully sent

        Raises:
            ConnectionError: If the connection is closed or sending fail
            ValueError: If the data is not in bytes format
            TimeoutError: If the send operation times out
        """
        pass

    @abstractmethod
    def receive(self, size, timeout=10):
        """
        Receive data from the communication channel.

        This method reads binary data from the configured connection.

        Args:
            size (int): Maximum number of bytes to receive
            timeout (float, optional): Read timeout in seconds.
                                       Defaults to 10.
                                       If None, uses the channel's
                                       default timeout.

        Returns:
            bytes: Data received from the connection

        Raises:
            ConnectionError: If the connection is closed or receiving
                             fails
            TimeoutError: If the receive operation times out
        """
        pass

    @abstractmethod
    def local_read(self, size):
        """
        Read data directly from the communication channel with minimal
        processing.

        This is a low-level method that bypasses most of the error
        handling and logging found in the standard receive method,
        providing direct access to the raw data stream.

        Args:
            size (int): Number of bytes to read from the channel

        Returns:
            bytes: The raw data read from the communication channel

        Raises:
            ConnectionError: If the connection is closed or reading fail
        """
        pass


class DataProcessor(ABC):
    """
    Interface for components that process incoming data streams.

    DataProcessor implementations transform, filter, or analyze data
    from various sources such as sensors, communication channels,
    or other system components. These components typically implement
    domain-specific logic for interpreting and handling structured data.

    Implementing classes should define methods to process received data
    through appropriate handler functions or callbacks.
    """

    @abstractmethod
    def process_recv_data(self, data_handler):
        pass


class SensorInterface(ABC):
    """
    Interface for components that interact with physical or virtual
    sensors.

    SensorInterface implementations provide a consistent API for
    accessing data from various sensor types such as IMUs, GPS, cameras,
    or environmental sensors. These components handle sensor
    initialization, reading, and data conversion.

    Implementing classes abstract the underlying hardware-specific
    details and provide standardized access to sensor data throughout
    the system.
    """

    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def get_sensor_data(self):
        pass


class NavigationPlanner(ABC):
    """
    Interface for flight control and path planning components.

    NavigationPlanner implementations handle trajectory generation,
    position control, and maneuver execution. These components
    translate high-level navigation commands into specific motion
    primitives and control signals.

    Implementing classes should provide methods for basic flight
    operations and precise positioning or velocity control of
    the aerial vehicle.
    """

    @abstractmethod
    def takeoff(self):
        pass

    @abstractmethod
    def land(self):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def set_target_position(self, x: float, y: float, z: float):
        pass

    @abstractmethod
    def set_target_velocity(self, vx: float, vy: float, vz: float):
        pass


class VisionProcessor(ABC):
    """
    Interface for computer vision processing components.

    VisionProcessor implementations handle image acquisition,
    processing, and feature extraction tasks. These components work
    with camera feeds to identify visual markers, patterns, or
    objects in the environment.

    Implementing classes should provide methods for processing images
    and extracting specific types of visual data such as ArUco markers,
    QR codes, and color-based object recognition.
    """

    @abstractmethod
    def process_image(self, image):
        pass

    @abstractmethod
    def get_aruco_data(self):
        pass

    @abstractmethod
    def get_qr_data(self):
        pass

    @abstractmethod
    def get_color_data(self):
        pass


class ManagerInterface(ABC):
    """
    Interface for system management and coordination components.

    The ManagerInterface defines a common API for components that
    oversee the lifecycle and coordination of multiple services
    or subsystems. Managers typically handle initialization sequences,
    monitor operational status, and ensure proper shutdown procedures.

    Implementing classes act as high-level controllers that maintain
    system state and orchestrate interactions between various components
    """

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass

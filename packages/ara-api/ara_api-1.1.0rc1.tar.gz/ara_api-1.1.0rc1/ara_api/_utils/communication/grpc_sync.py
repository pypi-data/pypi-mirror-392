import os
import threading
from typing import ClassVar, Dict, Optional

import grpc

from ara_api._utils.communication.gRPC.messages.base_msg_pb2 import (
    get_request,
)
from ara_api._utils.communication.gRPC.msp_pb2_grpc import MSPManagerStub
from ara_api._utils.communication.gRPC.navigation_pb2_grpc import (
    NavigationManagerStub,
)
from ara_api._utils.communication.gRPC.vision_pb2_grpc import VisionManagerStub
from ara_api._utils.config import (
    LOGGER_CONFIG,
    MSPConfigGRPC,
    NavigationConfigGRPC,
    VisionConfigGRPC,
)
from ara_api._utils.data import (
    IMU,
    Altitude,
    Analog,
    ArucoArray,
    Attitude,
    BlobArray,
    Image,
    ImageStream,
    Motor,
    OpticalFlow,
    Position,
    QRCodeArray,
    Sonar,
)
from ara_api._utils.data.msp.velocity import Velocity
from ara_api._utils.logger import Logger


class gRPCSync:
    _instance: ClassVar[Dict[int, "gRPCSync"]] = {}
    _creation_lock: ClassVar[threading.Lock] = threading.Lock()
    _logger = Logger(
        log_level=LOGGER_CONFIG.LOG_LEVEL,
        log_to_file=LOGGER_CONFIG.LOG_TO_FILE,
        log_to_terminal=LOGGER_CONFIG.LOG_TO_TERMINAL,
        log_dir=LOGGER_CONFIG.LOG_DIR,
    )

    def __new__(cls) -> "gRPCSync":
        process_id = os.getpid()

        if process_id not in cls._instance:
            with cls._creation_lock:
                if process_id not in cls._instance:
                    instance = super().__new__(cls)
                    cls._instance[process_id] = instance
                    cls._logger.debug(
                        "gRPCSync instance created for"
                        " process ID: {process_id}".format(
                            process_id=process_id
                        )
                    )

        return cls._instance[process_id]

    def __init__(self):
        if hasattr(self, "_initialized"):
            self._logger.debug(
                "gRPCSync instance already "
                "initialized for process ID: {process_id}".format(
                    process_id=os.getpid()
                )
            )
            return

        try:
            self._init_msp_connection()
            self._init_navigation_connection()
            self._init_vision_connection()

        except Exception as e:
            self._logger.error(f"Failed to initialize gRPC connections: {e}")
            self._cleanup_all_connections()

        self._initialized: bool = True

    def __del__(self):
        try:
            self._cleanup_all_connections()
        except Exception:
            pass  # Skip cleanup errors

    def _init_msp_connection(self) -> None:
        msp_address: str = MSPConfigGRPC.HOST + ":" + MSPConfigGRPC.PORT

        self._msp_channel = grpc.insecure_channel(msp_address)
        self._msp_stub = MSPManagerStub(self._msp_channel)

        self._logger.debug(
            "gRPCSync MSP connection initialized"
            " with address: {msp_address}".format(msp_address=msp_address)
        )

    def _init_navigation_connection(self) -> None:
        navigation_address: str = (
            NavigationConfigGRPC.HOST + ":" + NavigationConfigGRPC.PORT
        )

        self._navigation_channel = grpc.insecure_channel(navigation_address)
        self._navigation_stub = NavigationManagerStub(self._navigation_channel)

        self._logger.debug(
            "gRPCSync Navigation connection initialized"
            " with address: {navigation_address}".format(
                navigation_address=navigation_address
            )
        )

    def _init_vision_connection(self) -> None:
        vision_address: str = (
            VisionConfigGRPC.HOST + ":" + VisionConfigGRPC.PORT
        )

        self._vision_channel = grpc.insecure_channel(vision_address)
        self._vision_stub = VisionManagerStub(self._vision_channel)

        self._logger.debug(
            "gRPCSync Vision connection initialized"
            " with address: {vision_address}".format(
                vision_address=vision_address
            )
        )

    def _cleanup_all_connections(self) -> None:
        channels = [
            getattr(self, "_msp_channel", None),
            getattr(self, "_navigation_channel", None),
            getattr(self, "_vision_channel", None),
        ]

        for channel in channels:
            if channel:
                try:
                    channel.close()
                except Exception:
                    self._logger.error(
                        "gRPCSync cleanup failed for"
                        " process ID: {process_id}".format(
                            process_id=os.getpid()
                        )
                    )

    @classmethod
    def get_instance(cls) -> "gRPCSync":
        return cls()

    def msp_get_raw_imu(self) -> Optional[IMU]:
        try:
            response = self._msp_stub.get_raw_imu_rpc(
                get_request(req="SyncCall")
            )
            _imu = IMU()
            _imu.sync(response)

            return _imu
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_motor(self) -> Optional[Motor]:
        try:
            response = self._msp_stub.get_motor_rpc(
                get_request(req="SyncCall")
            )
            _motor = Motor()
            _motor.sync(response)

            return _motor
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_attitude(self) -> Optional[Attitude]:
        try:
            response = self._msp_stub.get_attitude_rpc(
                get_request(req="SyncCall")
            )
            _attitude = Attitude()
            _attitude.sync(response)

            return _attitude
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_altitude(self) -> Optional[Altitude]:
        try:
            response = self._msp_stub.get_altitude_rpc(
                get_request(req="SyncCall")
            )
            _altitude = Altitude()
            _altitude.sync(response)

            return _altitude
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_sonar(self) -> Optional[Sonar]:
        try:
            response = self._msp_stub.get_sonar_rpc(
                get_request(req="SyncCall")
            )
            _sonar = Sonar()
            _sonar.sync(response)

            return _sonar
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_optical_flow(self) -> Optional[OpticalFlow]:
        try:
            response = self._msp_stub.get_optical_flow_rpc(
                get_request(req="SyncCall")
            )
            _optical_flow = OpticalFlow()
            _optical_flow.sync(response)

            return _optical_flow
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_position(self) -> Optional[Position]:
        try:
            response = self._msp_stub.get_position_rpc(
                get_request(req="SyncCall")
            )
            _position = Position()
            _position.sync(response)

            return _position
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_velocity(self) -> Optional[Velocity]:
        try:
            response = self._msp_stub.get_velocity_rpc(
                get_request(req="SyncCall")
            )
            _velocity = Velocity()
            _velocity.sync(response)

            return _velocity
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_get_analog(self) -> Optional[Analog]:
        try:
            response = self._msp_stub.get_analog_rpc(
                get_request(req="SyncCall")
            )
            _analog = Analog()
            _analog.sync(response)

            return _analog
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def msp_cmd_send_rc(self, request, context) -> None:
        try:
            self._msp_stub.cmd_send_rc_rpc(request)
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")

    def msp_cmd_zero_position(self, request, context) -> None:
        try:
            self._msp_stub.cmd_zero_position_rpc(request)
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")

    def nav_cmd_takeoff(self, request, context) -> None:
        try:
            return self._navigation_stub.cmd_takeoff_rpc(
                request, metadata=context
            )
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")

    def nav_cmd_land(self, request, context) -> None:
        try:
            return self._navigation_stub.cmd_land_rpc(
                request, metadata=context
            )
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")

    def nav_cmd_move(self, request, context) -> None:
        try:
            return self._navigation_stub.cmd_move_rpc(
                request, metadata=context
            )
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")

    def nav_cmd_velocity(self, request, context) -> None:
        try:
            return self._navigation_stub.cmd_velocity_rpc(
                request, metadata=context
            )
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")

    def nav_cmd_altitude(self, request, context) -> None:
        try:
            return self._navigation_stub.cmd_altitude_rpc(
                request, metadata=context
            )
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")

    def vision_get_image(self) -> Optional[Image]:
        try:
            response = self._vision_stub.get_image_rpc(
                get_request(req="SyncCall")
            )
            _image = Image()
            _image.sync(response)

            return _image
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def vision_get_image_stream(self) -> Optional[ImageStream]:
        try:
            response = self._vision_stub.get_image_stream_rpc(
                get_request(req="SyncCall")
            )
            _image_stream = ImageStream()
            _image_stream.sync(response)

            return _image_stream
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def vision_get_aruco(self) -> Optional[ArucoArray]:
        try:
            response = self._vision_stub.get_aruco_rpc(
                get_request(req="SyncCall")
            )
            _aruco_array = ArucoArray()
            _aruco_array.sync(response)

            return _aruco_array
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def vision_get_qr_code(self) -> Optional[QRCodeArray]:
        try:
            response = self._vision_stub.get_qr_rpc(
                get_request(req="SyncCall")
            )
            _qr_code_array = QRCodeArray()
            _qr_code_array.sync(response)

            return _qr_code_array
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

    def vision_get_blob(self) -> Optional[BlobArray]:
        try:
            response = self._vision_stub.get_blob_rpc(
                get_request(req="SyncCall")
            )
            _blob_array = BlobArray()
            _blob_array.sync(response)

            return _blob_array
        except grpc.RpcError as e:
            self._logger.error(f"gRPC error: {e}")
            return None

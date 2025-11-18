# Communication module for ARA API
# Base messages
from ara_api._utils.communication.gRPC.messages.base_msg_pb2 import (
    command,
    get_request,
    status,
    vector2,
    vector3,
)

# MSP messages
from ara_api._utils.communication.gRPC.messages.msp_msg_pb2 import (
    altitude_data as altitude_grpc,
    analog_data as analog_grpc,
    attitude_data as attitude_grpc,
    flags_data as flags_grpc,
    imu_data as imu_grpc,
    motor_data as motor_grpc,
    optical_flow_data as optical_flow_grpc,
    position_data as position_grpc,
    rc_in as rc_in_grpc,
    sonar_data as sonar_grpc,
    velocity_data as velocity_grpc,
)

# TODO: Update and add new navigation messages
# Navigation messages
# from ara_api._communication.gRPC.messages.nav_msg_pb2 import *
# Vision messages
from ara_api._utils.communication.gRPC.messages.vision_msg_pb2 import (
    aruco as aruco_grpc,
    aruco_data_array as aruco_array_grpc,
    blob as blob_grpc,
    blob_data_array as blob_array_grpc,
    image_data as image_grpc,
    image_data_stream as image_stream_grpc,
    qr_code as qr_grpc,
    qr_data_array as qr_array_grpc,
)

# Service stub, servicer and add methods
from ara_api._utils.communication.gRPC.msp_pb2_grpc import (
    MSPManagerServicer as MSPServicer,
    MSPManagerStub as MSPStub,
    add_MSPManagerServicer_to_server as add_msp_to_server,
)
from ara_api._utils.communication.gRPC.navigation_pb2_grpc import (
    NavigationManagerServicer as NavigationServicer,
    NavigationManagerStub as NavigationStub,
    add_NavigationManagerServicer_to_server as add_navigation_to_server,
)
from ara_api._utils.communication.gRPC.vision_pb2_grpc import (
    VisionManagerServicer as VisionServicer,
    VisionManagerStub as VisionStub,
    add_VisionManagerServicer_to_server as add_vision_to_server,
)
from ara_api._utils.communication.grpc_sync import gRPCSync
from ara_api._utils.communication.websocket_sync import WebSocketFetcher

__all__ = [
    # Communication Fetchers
    "gRPCSync",
    "WebSocketFetcher",
    # Base messages
    "status",
    "command",
    "get_request",
    "vector3",
    "vector2",
    # MSP messages
    "motor_grpc",
    "imu_grpc",
    "attitude_grpc",
    "altitude_grpc",
    "sonar_grpc",
    "optical_flow_grpc",
    "position_grpc",
    "velocity_grpc",
    "analog_grpc",
    "flags_grpc",
    "rc_in_grpc",
    # Navigation messages
    # "nav_grpc",
    # Vision messages
    "image_grpc",
    "image_stream_grpc",
    "aruco_grpc",
    "qr_grpc",
    "blob_grpc",
    "aruco_array_grpc",
    "qr_array_grpc",
    "blob_array_grpc",
    # Service stub, servicer and add methods
    "MSPStub",
    "MSPServicer",
    "add_msp_to_server",
    "NavigationStub",
    "NavigationServicer",
    "add_navigation_to_server",
    "VisionStub",
    "VisionServicer",
    "add_vision_to_server",
]

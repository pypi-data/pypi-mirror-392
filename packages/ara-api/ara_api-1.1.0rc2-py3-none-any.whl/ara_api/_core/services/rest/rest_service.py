import multiprocessing as mp
import signal
import sys
from typing import Optional, Union

import grpc
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ara_api._core.services.rest.models import (
    AltitudeResponse,
    AttitudeResponse,
    BatteryResponse,
    IMUResponse,
    LandRequest,
    MotorResponse,
    MoveRequest,
    PositionResponse,
    StatusResponse,
    TakeoffRequest,
    VelocityRequest,
)
from ara_api._utils import (
    Altitude,
    Logger,
    get_request,
    gRPCSync,
    vector2,
    vector3,
)
from ara_api._utils.config import LOGGER_CONFIG
from ara_api._utils.data.msp import imu
from ara_api._utils.data.msp.motor import Motor

app: Optional[FastAPI] = None
grpc_client: Optional[gRPCSync] = None
logger: Optional[Logger] = None


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI instance.
    """
    fastapi_app = FastAPI(
        title="ARA API REST Interface",
        description="REST API wrapper for ARA drone control system",
        version="1.0.0",  # ! VERSION HARD
    )

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @fastapi_app.get("/")
    async def root() -> dict:
        """Root endpoint providing API information."""
        return {
            "service": "ARA API REST Interface",
            "version": "1.0.0",  # ! VERSION HARD
            "status": "running",
        }

    @fastapi_app.post("/api/navigation/takeoff", response_model=StatusResponse)
    async def takeoff(request: TakeoffRequest) -> StatusResponse:
        """
        Command drone to takeoff to specified altitude.

        Args:
            request: Takeoff request with target altitude.

        Returns:
            Status of the takeoff command.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            logger.info(
                f"Takeoff command received: altitude={request.altitude}"
            )

            altitude_msg = Altitude(alt=request.altitude)
            grpc_client.nav_cmd_takeoff(
                altitude_msg.grpc,
                [],
            )

            return StatusResponse(
                status="success",
                details=f"Takeoff to {request.altitude}m initiated",
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in takeoff: {e}")
            raise HTTPException(
                status_code=500, detail=f"gRPC error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in takeoff: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @fastapi_app.post("/api/navigation/land", response_model=StatusResponse)
    async def land(request: LandRequest) -> StatusResponse:
        """
        Command drone to land.

        Args:
            request: Empty land request.

        Returns:
            Status of the land command.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            logger.info("Land command received")

            grpc_client.nav_cmd_land(
                get_request(req="REST"),
                [],
            )

            return StatusResponse(
                status="success", details="Landing initiated"
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in land: {e}")
            raise HTTPException(
                status_code=500, detail=f"gRPC error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in land: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @fastapi_app.post("/api/navigation/move", response_model=StatusResponse)
    async def move(request: MoveRequest) -> StatusResponse:
        """
        Command drone to move to specified position.

        Args:
            request: Move request with target coordinates.

        Returns:
            Status of the move command.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            logger.info(
                f"Move command received: x={request.x}, "
                f"y={request.y}, z={request.z}"
            )

            position_msg = vector3(x=request.x, y=request.y, z=request.z)
            grpc_client.nav_cmd_move(position_msg, [])

            coords = f"({request.x}, {request.y}, {request.z})"
            return StatusResponse(
                status="success",
                details=f"Move to {coords} initiated",
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in move: {e}")
            raise HTTPException(
                status_code=500, detail=f"gRPC error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in move: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @fastapi_app.post("/api/navigation/speed", response_model=StatusResponse)
    async def speed(request: VelocityRequest) -> StatusResponse:
        """
        Command drone to move with specified velocity.

        Args:
            request: Velocity request with x and y components.

        Returns:
            Status of the velocity command.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            logger.info(
                f"Velocity command received: vx={request.vx}, vy={request.vy}"
            )

            velocity_msg = vector2(x=request.vx, y=request.vy)
            grpc_client.nav_cmd_velocity(velocity_msg, [])

            vel_str = f"({request.vx}, {request.vy})"
            return StatusResponse(
                status="success",
                details=f"Velocity command {vel_str} initiated",
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in velocity: {e}")
            raise HTTPException(
                status_code=500, detail=f"gRPC error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in velocity: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @fastapi_app.get("/api/msp/imu", response_model=IMUResponse)
    async def get_imu() -> IMUResponse:
        """
        Get current drone IMU data.

        Returns:
            Current imu or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            imu_data: Union[imu.IMU, None] = grpc_client.msp_get_raw_imu()

            if imu_data is None:
                return IMUResponse(error="Failed to retrieve imu")

            return IMUResponse(
                gyro_x=imu_data.grpc.gyro.x,
                gyro_y=imu_data.grpc.gyro.y,
                gyro_z=imu_data.grpc.gyro.z,
                acc_x=imu_data.grpc.acc.x,
                acc_y=imu_data.grpc.acc.y,
                acc_z=imu_data.grpc.acc.z,
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_imu: {e}")
            return IMUResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_imu: {e}")
            return IMUResponse(error=str(e))

    @fastapi_app.get("/api/msp/motor", response_model=MotorResponse)
    async def get_motor() -> MotorResponse:
        """
        Get current drone motor data.

        Returns:
            Current motor data or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            motor_data: Union[Motor, None] = grpc_client.msp_get_motor()

            if motor_data is None:
                return MotorResponse(error="Failed to retrieve motor")

            return MotorResponse(data=motor_data.grpc)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_motor: {e}")
            return MotorResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_motor: {e}")
            return MotorResponse(error=str(e))

    @fastapi_app.get("/api/msp/attitude", response_model=AttitudeResponse)
    async def get_attitude() -> AttitudeResponse:
        """
        Get current drone attitude (roll, pitch, yaw).

        Returns:
            Current attitude or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            attitude_data = grpc_client.msp_get_attitude()

            if attitude_data is None:
                return AttitudeResponse(error="Failed to retrieve attitude")

            return AttitudeResponse(
                roll=attitude_data.json["roll"],
                pitch=attitude_data.json["pitch"],
                yaw=attitude_data.json["yaw"],
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_attitude: {e}")
            return AttitudeResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_attitude: {e}")
            return AttitudeResponse(error=str(e))

    @fastapi_app.get("/api/msp/altitude", response_model=AltitudeResponse)
    async def get_altitude() -> AltitudeResponse:
        """
        Get current drone altitude.

        Returns:
            Current altitude or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            altitude_data = grpc_client.msp_get_altitude()

            if altitude_data is None:
                return AltitudeResponse(error="Failed to retrieve altitude")

            return AltitudeResponse(altitude=altitude_data.alt)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_altitude: {e}")
            return AltitudeResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_altitude: {e}")
            return AltitudeResponse(error=str(e))

    @fastapi_app.get("/api/msp/sonar", response_model=AltitudeResponse)
    async def get_sonar() -> AltitudeResponse:
        """
        Get current drone altitude.

        Returns:
            Current altitude or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            sonar_data = grpc_client.msp_get_sonar()

            if sonar_data is None:
                return AltitudeResponse(error="Failed to retrieve sonar")

            return AltitudeResponse(altitude=sonar_data.alt)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_sonar: {e}")
            return AltitudeResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_altitude: {e}")
            return AltitudeResponse(error=str(e))

    @fastapi_app.get("/api/msp/optical_flow", response_model=AltitudeResponse)
    async def get_optical_flow() -> AltitudeResponse:
        """
        Get current drone altitude.

        Returns:
            Current altitude or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            optical_flow_data = grpc_client.msp_get_optical_flow()

            if optical_flow_data is None:
                return AltitudeResponse(
                    error="Failed to retrieve optical_flow"
                )

            return AltitudeResponse(altitude=optical_flow_data.alt)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_altitude: {e}")
            return AltitudeResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_altitude: {e}")
            return AltitudeResponse(error=str(e))

    @fastapi_app.get("/api/msp/position", response_model=PositionResponse)
    async def get_position() -> PositionResponse:
        """
        Get current drone position.

        Returns:
            Current position or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            position_data = grpc_client.msp_get_position()

            if position_data is None:
                return PositionResponse(error="Failed to retrieve position")

            return PositionResponse(
                x=position_data.json["x"],
                y=position_data.json["y"],
                z=position_data.json["z"],
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_position: {e}")
            return PositionResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_position: {e}")
            return PositionResponse(error=str(e))

    @fastapi_app.get("/api/msp/position", response_model=PositionResponse)
    async def get_position() -> PositionResponse:
        """
        Get current drone position.

        Returns:
            Current position or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            position_data = grpc_client.msp_get_position()

            if position_data is None:
                return PositionResponse(error="Failed to retrieve position")

            return PositionResponse(
                x=position_data.json["x"],
                y=position_data.json["y"],
                z=position_data.json["z"],
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_position: {e}")
            return PositionResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_position: {e}")
            return PositionResponse(error=str(e))

    @fastapi_app.get("/api/msp/battery", response_model=BatteryResponse)
    async def get_battery() -> BatteryResponse:
        """
        Get current battery information.

        Returns:
            Battery data or error.
        """
        try:
            if grpc_client is None:
                raise HTTPException(
                    status_code=500, detail="gRPC client not initialized"
                )

            analog_data = grpc_client.msp_get_analog()

            if analog_data is None:
                return BatteryResponse(error="Failed to retrieve battery data")

            return BatteryResponse(
                voltage=analog_data.json.get("vbat", 0.0),
                cell_count=None,
                capacity=None,
            )
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_battery: {e}")
            return BatteryResponse(error=f"gRPC error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_battery: {e}")
            return BatteryResponse(error=str(e))

    return fastapi_app


class RESTAPIProcess(mp.Process):
    """REST API Process for ARA drone control system."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Initialize REST API Process.

        Args:
            host: Host address to bind the server.
            port: Port number for the server.
        """
        super().__init__(name="RESTAPIProcess")
        self.host = host
        self.port = port
        self.logger: Optional[Logger] = None
        self._shutdown_event = mp.Event()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        if self.logger:
            self.logger.info(
                f"Received signal {signum}, initiating graceful shutdown"
            )
        self._shutdown_event.set()
        sys.exit(0)

    def run(self) -> None:
        """
        Run the REST API server process.

        Initializes logger and gRPC client, then starts FastAPI
        server.
        """
        global app, grpc_client, logger

        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.logger = Logger(
            log_level=LOGGER_CONFIG.LOG_LEVEL,
            log_to_file=LOGGER_CONFIG.LOG_TO_FILE,
            log_to_terminal=LOGGER_CONFIG.LOG_TO_TERMINAL,
            log_dir=LOGGER_CONFIG.LOG_DIR,
        )
        logger = self.logger

        self.logger.info(
            f"Starting REST API server on {self.host}:{self.port}"
        )

        try:
            grpc_client = gRPCSync()
            self.logger.info("gRPCSync client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize gRPCSync: {e}")
            return

        app = create_app()

        try:
            uvicorn.run(
                app,
                host=self.host,
                port=self.port,
                log_level="info",
            )
        except Exception as e:
            self.logger.error(f"Error running REST API server: {e}")
        finally:
            self.logger.info("REST API server stopped")


if __name__ == "__main__":
    process = RESTAPIProcess(host="0.0.0.0", port=50054)
    process.start()

    try:
        process.join()
    except KeyboardInterrupt:
        print("\nShutting down REST API server...")
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
        print("REST API server stopped")

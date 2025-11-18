import asyncio
import threading
from typing import Union

import grpc.aio as grpc_aio

from ara_api._core.services.msp.connection import (
    ConnectionManager,
)
from ara_api._core.services.msp.controller import MSPController
from ara_api._core.services.msp.telemetry import (
    AltitudeReader,
    AnalogReader,
    AttitudeReader,
    IMUReader,
    MotorReader,
    OpticalFlowReader,
    PositionReader,
    SonarReader,
    TelemetryRegistry,
    TelemetryScheduler,
    VelocityReader,
)
from ara_api._utils import (
    IMU,
    RC,
    Altitude,
    Analog,
    Attitude,
    Logger,
    Motor,
    MSPServicer,
    OpticalFlow,
    Position,
    Sonar,
    add_msp_to_server,
    status,
)
from ara_api._utils.config import FREQUENCY
from ara_api._utils.data.msp.velocity import Velocity


class MSPManager(MSPServicer):
    def __init__(
        self,
        mode: str = "TCP",
        link: Union[tuple, str] = "",
        analyzer_flag: bool = False,
        log: bool = True,
        output: bool = True,
    ) -> None:
        self.logger = Logger(log_to_file=log, log_to_terminal=True)

        self.connection_manager = ConnectionManager(mode, link)
        if not self.connection_manager.connect():
            raise Exception("Failed to connect to MSP device")

        self.controller = MSPController(
            self.connection_manager.get_transmitter(), log, output
        )

        self.imu = IMU()
        self.motor = Motor()
        self.attitude = Attitude()
        self.altitude = Altitude()
        self.sonar = Sonar()
        self.optical_flow = OpticalFlow()
        self.position = Position()
        self.velocity = Velocity()
        self.analog = Analog()
        self.rc_in = RC()

        self.registry = TelemetryRegistry()
        self._register_telemetry_readers()

        self.scheduler = TelemetryScheduler(self.registry)
        self._update_thread = None

    def _register_telemetry_readers(self) -> None:
        readers = [
            (MotorReader(self.controller, self.motor), FREQUENCY["MOTOR"]),
            (IMUReader(self.controller, self.imu), FREQUENCY["IMU"]),
            (
                AttitudeReader(self.controller, self.attitude),
                FREQUENCY["ATTITUDE"],
            ),
            (
                AltitudeReader(self.controller, self.altitude),
                FREQUENCY["ALTITUDE"],
            ),
            (SonarReader(self.controller, self.sonar), FREQUENCY["SONAR"]),
            (
                OpticalFlowReader(self.controller, self.optical_flow),
                FREQUENCY["OPTICAL_FLOW"],
            ),
            (
                PositionReader(self.controller, self.position),
                FREQUENCY["POSITION"],
            ),
            (
                VelocityReader(self.controller, self.velocity),
                FREQUENCY["VELOCITY"],
            ),
            (AnalogReader(self.controller, self.analog), FREQUENCY["ANALOG"]),
        ]

        for reader, frequency in readers:
            self.registry.register(reader, frequency)

    async def get_raw_imu_rpc(self, _request, context) -> IMU:
        try:
            self.logger.debug(f"[IMU]: request from client: {context.peer()}")
            return self.imu.grpc
        except Exception as e:
            self.logger.error(f"[IMU]: Error in sending response: {e}")
            return self.imu

    async def get_motor_rpc(self, _request, context) -> Motor:
        try:
            self.logger.debug(
                f"[MOTOR]: request from client: {context.peer()}"
            )
            return self.motor.grpc
        except Exception as e:
            self.logger.error(f"[MOTOR]: Error in sending response: {e}")
            return self.motor

    async def get_attitude_rpc(self, _request, context) -> Attitude:
        try:
            self.logger.debug(
                f"[ATTITUDE]: request from client: {context.peer()}"
            )
            return self.attitude.grpc
        except Exception as e:
            self.logger.error(f"[ATTITUDE]: Error in sending response: {e}")
            return self.attitude

    async def get_altitude_rpc(self, _request, context) -> Altitude:
        try:
            self.logger.debug(
                f"[ALTITUDE]: request from client: {context.peer()}"
            )
            return self.altitude.grpc
        except Exception as e:
            self.logger.error(f"[ALTITUDE]: Error in sending response: {e}")
            return self.altitude

    async def get_sonar_rpc(self, _request, context) -> Sonar:
        try:
            self.logger.debug(
                f"[SONAR]: request from client: {context.peer()}"
            )
            return self.sonar.grpc
        except Exception as e:
            self.logger.error(f"[SONAR]: Error in sending response: {e}")
            return self.sonar

    async def get_optical_flow_rpc(self, _request, context) -> OpticalFlow:
        try:
            self.logger.debug(
                f"[OPTICAL_FLOW]: request from client: {context.peer()}"
            )
            return self.optical_flow.grpc
        except Exception as e:
            self.logger.error(
                f"[OPTICAL_FLOW]: Error in sending response: {e}"
            )
            return self.optical_flow

    async def get_position_rpc(self, _request, context) -> Position:
        try:
            self.logger.debug(
                f"[POSITION]: request from client: {context.peer()}"
            )
            return self.position.grpc
        except Exception as e:
            self.logger.error(f"[POSITION]: Error in sending response: {e}")
            return self.position

    async def get_velocity_rpc(self, _request, context) -> Velocity:
        try:
            self.logger.debug(
                f"[VELOCITY]: request from client: {context.peer()}"
            )
            return self.velocity.grpc
        except Exception as e:
            self.logger.error(f"[VELOCITY]: Error in sending response: {e}")
            return self.velocity

    async def get_analog_rpc(self, _request, context) -> Analog:
        try:
            self.logger.debug(
                f"[ANALOG]: request from client: {context.peer()}"
            )
            return self.analog.grpc
        except Exception as e:
            self.logger.error(f"[ANALOG]: Error in sending response: {e}")
            return self.analog

    async def cmd_send_rc_rpc(self, request, context) -> RC:
        return super().cmd_send_rc_rpc(request, context)

    async def cmd_zero_position_rpc(self, request, context) -> status:
        return super().cmd_zero_position_rpc(request, context)

    def start_update_loop(self) -> None:
        if self._update_thread is None or not self._update_thread.is_alive():
            self._update_thread = threading.Thread(
                target=self._update_loop, daemon=False
            )
            self._update_thread.start()
            self.logger.info("[MSPManager] Update loop started")

    def stop_update_loop(self) -> None:
        self.scheduler.stop()
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=5)
            self.logger.info("[MSPManager] Update loop stopped")

    def _update_loop(self) -> None:
        self.scheduler.start()
        while self.scheduler.is_running():
            try:
                self.scheduler.update_cycle()
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")


async def serve(manager: MSPManager) -> None:
    server = grpc_aio.server()
    add_msp_to_server(manager, server)
    listen_address = "[::]:50051"
    server.add_insecure_port(listen_address)

    manager.logger.info(f"Starting gRPC server on {listen_address}")
    await server.start()
    manager.logger.info("gRPC server started successfully.")

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        manager.logger.info("gRPC server stopped by user.")
    finally:
        manager.logger.info("Shutting down gRPC server...")
        await server.stop(grace=5.0)


def main(*_args, **_kwargs) -> None:  # noqa: ARG001
    manager = MSPManager(mode="TCP", link=("192.168.2.113", 5760))
    try:
        manager.start_update_loop()

        asyncio.run(serve(manager))
    except KeyboardInterrupt:
        print("Server stopped by user.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if manager:
            print("Stopping update loop...")
            manager.stop_update_loop()
            print("Server shutdown complete.")


if __name__ == "__main__":
    main()

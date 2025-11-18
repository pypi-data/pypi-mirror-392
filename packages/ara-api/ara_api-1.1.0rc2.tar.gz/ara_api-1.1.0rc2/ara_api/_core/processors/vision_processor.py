import multiprocessing
import signal
import sys
from concurrent import futures

import grpc

from ara_api._core.services.vision.vision_service import VisionManager


class VisionManagerProcess(multiprocessing.Process):
    """Vision manager process class.

    This class runs the VisionManager service in a separate process
    to prevent OpenCV multiprocessing issues.
    """

    def __init__(
        self,
        camera_url: str = "0",
        grpc_port: int = 50053,
        enable_logging: bool = True,
        enable_output: bool = True,
        max_workers: int = 4,
    ):
        super().__init__()

        self._camera_url = camera_url
        self._grpc_port = grpc_port
        self._enable_logging = enable_logging
        self._enable_output = enable_output
        self._max_workers = max_workers

        self._grpc_options = [
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.http2.min_time_between_pings_ms", 10000),
            ("grpc.http2.min_ping_interval_without_data_ms", 300000),
        ]

        self._stop_event = multiprocessing.Event()
        self._ready_event = multiprocessing.Event()
        self._error_event = multiprocessing.Event()

        self.daemon = True

    def run(self) -> None:
        # Создаем логгер в новом процессе
        from ara_api._utils import Logger

        self._logger = Logger(
            log_to_file=self._enable_logging,
            log_to_terminal=self._enable_output,
        )

        try:
            self._logger.debug("Starting VisionManagerProcess")

            import cv2

            cv2.setNumThreads(0)  # Disable OpenCV multithreading
            self._logger.debug(
                "OpenCV configured for single-threaded operation"
            )

            self._setup_signal_handlers()

            self._run_grpc_server()

        except Exception as e:
            self._logger.error(
                "Critical error in VisionManagerProcess: {e}".format(e=e)
            )

            self._error_event.set()
            sys.exit(1)

        finally:
            self._logger.info("VisionManagerProcess has stopped")

    def _setup_signal_handlers(self) -> None:
        def signal_handler(signum: int, frame) -> None:
            self._logger.info(
                f"Received signal {signum}, stopping VisionManagerProcess"
            )
            self.stop()

        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, signal_handler)

    def _run_grpc_server(self) -> None:
        vision_manager = None
        server = None

        try:
            server = grpc.server(
                futures.ThreadPoolExecutor(max_workers=self._max_workers),
                options=self._grpc_options,
            )

            vision_manager = VisionManager(
                log=self._enable_logging,
                output=self._enable_output,
            )

            if not vision_manager.initialize(url=self._camera_url):
                self._logger.error("Failed to initialize VisionManager")
                self._error_event.set()
                return

            from ara_api._utils import add_vision_to_server

            add_vision_to_server(vision_manager, server)

            address = "[::]:{port}".format(port=self._grpc_port)
            server.add_insecure_port(address)
            server.start()

            self._logger.info(
                "gRPC server started on port {port}".format(
                    port=self._grpc_port
                )
            )

            self._ready_event.set()

            try:
                while not self._stop_event.is_set():
                    self._stop_event.wait(timeout=0.5)
            except KeyboardInterrupt:
                self._logger.info(
                    "KeyboardInterrupt received, stopping server"
                )
        except Exception as e:
            self._logger.error(f"Error starting VisionManagerProcess: {e}")
            self._error_event.set()
        finally:
            self._logger.info("Shutting down gRPC server")

            if server:
                try:
                    server.stop(grace=2)
                    self._logger.debug("gRPC server stopped")
                except Exception as e:
                    self._logger.error(f"Error stopping gRPC server: {e}")

    def stop(self) -> None:
        if self._logger:
            self._logger.info("Stopping VisionManagerProcess")
        self._stop_event.set()

    @property
    def is_ready(self) -> bool:
        return self._ready_event.is_set() and not self._error_event.is_set()

    @property
    def has_error(self) -> bool:
        return self._error_event.is_set()

    def wait_for_ready(self, timeout: float = 10.0) -> bool:
        return self._ready_event.wait(timeout)

import asyncio
import contextlib
import functools
import multiprocessing
import signal
import threading
from typing import Optional, Union

import grpc.aio as grpc_aio

from ara_api._core.services import MSPManager
from ara_api._utils import Logger, add_msp_to_server


class MSPManagerProcess(multiprocessing.Process):
    """
    Process wrapper for MSPManager with integrated gRPC server.

    Runs MSPManager and its update loop in a separate process with
    a gRPC server to provide remote access to MSP data. Implements
    proper lifecycle management even when running as a daemon process.
    """

    def __init__(
        self,
        mode: str = "TCP",
        link: Union[tuple, str] = "",
        analyzer_flag: bool = False,
        log: bool = False,
        output: bool = False,
        grpc_address: str = "[::]:50051",
        name: str = "MSPManagerProcess",
    ) -> None:
        """
        Initialize the MSP Manager Process.

        Args:
            mode: Connection mode ("TCP" or "SERIAL")
            link: Connection reference (tuple for TCP, str for Serial)
            analyzer_flag: Whether to enable analyzer
            log: Whether to log messages
            output: Whether to print output
            grpc_address: Address to bind the gRPC server
            name: Name of the process
        """
        super().__init__(name=name, daemon=False)

        # Сохраняем параметры логгера для создания в run()
        self._log_to_file = log
        self._log_to_terminal = output

        self._mode = mode
        self._link = link
        self._analyzer_flag = analyzer_flag
        self._log = log
        self._output = output
        self._grpc_address = grpc_address

        self._msp_manager: Optional[MSPManager] = None
        self._server: Optional[grpc_aio.Server] = None
        self._stop_event = multiprocessing.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def run(self) -> None:
        """
        Run the MSP Manager process.

        This method is called when the process starts. It initializes
        the MSPManager, sets up the async event loop, and starts the
        gRPC server.
        """
        # Создаем логгер в новом процессе
        self.logger = Logger(
            log_to_file=self._log_to_file,
            log_to_terminal=self._log_to_terminal
        )

        try:
            import setproctitle

            setproctitle.setproctitle(f"python-{self.name}")
        except ImportError:
            pass

        self.logger.info(f"Starting {self.name} process")

        try:
            self._msp_manager = MSPManager(
                mode=self._mode,
                link=self._link,
                analyzer_flag=self._analyzer_flag,
                log=self._log,
                output=self._output,
            )

            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            self._setup_signal_handlers()

            self._run_update_thread()

            self._loop.run_until_complete(self._run_grpc_server())

        except Exception as e:
            self.logger.error(f"Error in {self.name}: {e}")
            import traceback

            self.logger.error(traceback.format_exc())
        finally:
            self._cleanup_resources()

    def _run_update_thread(self) -> None:
        """Run the MSP update loop with proper exception handling."""
        if not self._msp_manager:
            self.logger.error("MSP manager not initialized")
            return

        try:
            self._msp_manager.start_update_loop()
            self.logger.info("MSP update loop started successfully")
        except Exception as e:
            self.logger.error(f"Error in MSP update loop: {e}")
            self._stop_event.set()

    async def _run_grpc_server(self) -> None:
        """Initialize and run the gRPC server."""
        if not self._msp_manager:
            raise RuntimeError("MSP manager not initialized")

        self._server = grpc_aio.server(
            options=[
                ("grpc.max_send_message_length", 10 * 1024 * 1024),
                ("grpc.max_receive_message_length", 10 * 1024 * 1024),
                ("grpc.keepalive_time_ms", 30000),
                ("grpc.keepalive_timeout_ms", 5000),
                ("grpc.keepalive_permit_without_calls", True),
                ("grpc.http2.max_pings_without_data", 0),
                ("grpc.http2.min_time_between_pings_ms", 10000),
            ]
        )

        add_msp_to_server(self._msp_manager, self._server)

        self._server.add_insecure_port(self._grpc_address)
        await self._server.start()
        self.logger.info(f"gRPC server listening on {self._grpc_address}")

        await self._wait_for_termination()

    async def _wait_for_termination(self) -> None:
        """Wait for termination event with periodic checks."""
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(0.5)

            self.logger.info("Termination event set, shutting down server")
        except asyncio.CancelledError:
            self.logger.info("Server wait task cancelled")
        finally:
            await self._shutdown_server()

    async def _shutdown_server(self) -> None:
        if self._server:
            self.logger.info("Stopping gRPC server...")
            try:
                await self._server.stop(grace=5.0)
                self.logger.info("gRPC server stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping gRPC server: {e}")

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        if not self._loop:
            return

        for sig_name in ("SIGINT", "SIGTERM"):
            sig_num = getattr(signal, sig_name, None)
            if sig_num is None:
                continue

            self._loop.add_signal_handler(
                sig_num, functools.partial(self._handle_signal, sig_name)
            )

    def _handle_signal(self, sig_name: str) -> None:
        """Handle termination signal."""
        self.logger.info(f"Received {sig_name}, initiating shutdown")
        if not self._stop_event.is_set():
            self._stop_event.set()

    def _cleanup_resources(self) -> None:
        """Clean up resources during shutdown."""
        self.logger.info("Cleaning up resources")

        if self._msp_manager:
            try:
                self._msp_manager.stop_update_loop()
                self.logger.info("MSP update loop stopped")
            except Exception as e:
                self.logger.error(f"Error stopping MSP update loop: {e}")

        if self._loop and not self._loop.is_closed():
            try:
                pending_tasks = [
                    task
                    for task in asyncio.all_tasks(self._loop)
                    if not task.done()
                ]
                if pending_tasks:
                    self.logger.info(
                        f"Cancelling {len(pending_tasks)} pending tasks"
                    )
                    for task in pending_tasks:
                        task.cancel()

                    with contextlib.suppress(Exception):
                        self._loop.run_until_complete(
                            asyncio.gather(
                                *pending_tasks, return_exceptions=True
                            )
                        )
            except Exception as e:
                self.logger.error(f"Error cancelling pending tasks: {e}")

        self.logger.info(f"{self.name} process terminated")

    def stop(self) -> None:
        """
        Signal the process to stop.

        This can be called from the parent process to request
        termination.
        """
        self.logger.info(f"Stop requested for {self.name}")
        self._stop_event.set()

        if self._msp_manager:
            self._msp_manager.is_running = False

        if self.is_alive():
            self.join(timeout=5)

            if self.is_alive():
                self.logger.warning(
                    f"{self.name} did not terminate in time, forcing join"
                )
                self.terminate()
                self.join(timeout=5)

    @property
    def is_ready(self) -> bool:
        """
        Check if the process is ready.

        Returns:
            bool: True if the process is running and ready,
                  False otherwise.
        """
        return (
            self.is_alive()
            and self._msp_manager is not None
            and not self._stop_event.is_set()
        )

    @property
    def status(self) -> dict:
        """
        Get the current status of the process.

        Returns:
            dict: Status information about the process.
        """
        return {
            "process alive": self.is_alive(),
            "stop_event_set": self._stop_event.is_set(),
            "msp_manager_initialized": self._msp_manager is not None,
            "msp_running": (
                self._msp_manager.is_running if self._msp_manager else False
            ),
            "grpc_address": (self._grpc_address),
        }

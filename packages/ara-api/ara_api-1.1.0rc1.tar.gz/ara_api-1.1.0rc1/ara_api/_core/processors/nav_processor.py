import multiprocessing
import signal
import sys
from concurrent import futures

import grpc

from ara_api._core.services.nav.nav_service import NavigationManager
from ara_api._utils.config import NavigationConfigGRPC


class NavigationManagerProcess(multiprocessing.Process):
    def __init__(
        self,
        grpc_port: int = 0,
        enable_logging: bool = False,
        enable_output: bool = False,
        max_workers: int = 0,
    ):
        super().__init__()

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
            self._logger.debug("Запуск NavigationManagerProcess")

            self._setup_signal_handlers()

            self._run_grpc_server()

        except Exception as e:
            self._logger.error(
                "Критическая ошибка в NavigationManagerProcess: {e}".format(
                    e=e
                )
            )
            self._error_event.set()
            sys.exit(1)

        finally:
            self._logger.info("NavigationManagerProcess остановлен")

    def _setup_signal_handlers(self) -> None:
        def signal_handler(signum, frame):
            self._logger.info(
                "Получен сигнал {signum}, завершение "
                "процесса NavigationManagerProcess".format(signum=signum)
            )
            self.stop()

        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, signal_handler)

    def _run_grpc_server(self) -> None:
        navigation_manager = None
        server = None

        try:
            server = grpc.server(
                futures.ThreadPoolExecutor(max_workers=self._max_workers),
                options=self._grpc_options,
            )

            navigation_manager = NavigationManager(
                log=self._enable_logging, output=self._enable_output
            )

            if not navigation_manager.initialize():
                self._logger.error(
                    "Инициализация NavigationManager не удалась"
                )
                self._error_event.set()
                return

            from ara_api._utils import add_navigation_to_server

            add_navigation_to_server(navigation_manager, server)

            address = "[::]:{port}".format(port=self._grpc_port)
            server.add_insecure_port(address)
            server.start()

            self._logger.debug(
                "gRPC сервер навигации запущен на порту {port}".format(
                    port=self._grpc_port
                )
            )

            self._ready_event.set()

            try:
                while not self._stop_event.is_set():
                    self._stop_event.wait(timeout=0.5)
            except KeyboardInterrupt:
                self._logger.info(
                    "Получен KeyboardInterrupt, остановка gRPC сервера"
                )
        except Exception as e:
            self._logger.error(
                "Ошибка при запуске gRPC сервера: {e}".format(e=e)
            )
            self._error_event.set()

        finally:
            self._logger.info("Завершение работы gRPC сервера навигации")

            if server:
                try:
                    server.stop(grace=2)
                    self._logger.debug("gRPC сервер навигации остановлен")
                except Exception as e:
                    self._logger.error(
                        "Ошибка остановки gRPC сервера навигации: {e}".format(
                            e=e
                        )
                    )

    def stop(self) -> None:
        self._logger.info("Остановка NavigationManagerProcess")
        self._stop_event.set()

    @property
    def is_ready(self) -> bool:
        return self._ready_event.is_set() and not self._error_event.is_set()

    @property
    def has_error(self) -> bool:
        return self._error_event.is_set()

    def wait_for_ready(self, timeout: float = 10.0) -> bool:
        return self._ready_event.wait(timeout)

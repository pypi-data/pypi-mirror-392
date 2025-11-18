import argparse
import multiprocessing
import signal
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ara_api._core.processors import (
    MSPManagerProcess,
    NavigationManagerProcess,
    VisionManagerProcess,
)
from ara_api._core.services.rest import RESTAPIProcess
from ara_api._utils import Debugger, Logger, UIHelper
from ara_api._utils.config import (
    MSPConfigGRPC,
    NavigationConfigGRPC,
    VisionConfigGRPC,
)


class ProcessStatus(Enum):
    """Статусы процессов в системе."""

    NOT_STARTED = "not_started"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ProcessInfo:
    """Информация о процессе."""

    name: str
    process: multiprocessing.Process
    status: ProcessStatus
    start_time: Optional[float] = None
    error_message: Optional[str] = None


class ProcessManager(ABC):
    """Абстрактный базовый класс для управления процессами."""

    @abstractmethod
    def start(self) -> bool:
        """Запускает процесс."""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Останавливает процесс."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Проверяет состояние процесса."""
        pass


class ApplicationManager:
    def __init__(self):
        self.parser: argparse.ArgumentParser = self._setup_argparser()
        self.args: argparse.Namespace = self.parser.parse_args()

        # Создаем логгер для менеджера
        self._init_logger()

        self.dev_mode: bool = True
        self.debugger: Optional[Debugger] = None

        self._processes: Dict[str, ProcessInfo] = {}
        self._stop_event = multiprocessing.Event()
        self._running: bool = False

        self._ui_helper = UIHelper()

        self._logger.info("ApplicationManager инициализирован")

    def __getstate__(self) -> Dict[str, Any]:
        """Подготавливает объект для сериализации (pickle)."""
        state = self.__dict__.copy()
        # Удаляем логгер из состояния, так как он не может быть
        # сериализован
        state.pop("_logger", None)
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Восстанавливает объект после десериализации."""
        self.__dict__.update(state)
        # Пересоздаем логгер в новом процессе
        self._init_logger()

    def _init_logger(self) -> None:
        """Инициализирует логгер для менеджера."""
        self._logger = Logger(
            name="ApplicationManager",
            log_to_file=self.args.logging,
            log_to_terminal=self.args.sensor_output,
        )

    def _setup_argparser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description=(
                "Запуск приложения и сервисов "
                + "для автономного полета ARA MINI"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "--sensor-output",
            action="store_true",
            help="Вывод данных с датчиков в терминал ",
        )

        parser.add_argument(
            "--logging",
            action="store_true",
            help="Включение записи логов в файл",
        )
        parser.add_argument(
            "--docs", action="store_true", help="Отображение документации API"
        )
        parser.add_argument(
            "--analyzer",
            action="store_true",
            help="Режим анализатора - только чтение данных",
        )
        parser.add_argument(
            "--only-msp",
            action="store_true",
            help="Запуск только MSP сервиса без навигации и vision",
        )

        connection_group = parser.add_mutually_exclusive_group()
        connection_group.add_argument(
            "--serial",
            type=str,
            metavar="PORT",
            help="Подключение по Serial-порту (например: /dev/ttyACM0)",
        )
        connection_group.add_argument(
            "--ip",
            type=str,
            metavar="ADDRESS",
            help="IP-адрес для TCP-подключения (по умолчанию: 192.168.2.113)",
        )

        return parser

    def _determine_connection_config(
        self,
    ) -> Tuple[Optional[str], Optional[Any]]:
        if self.args.ip is not None:
            return "TCP", (self.args.ip, 5760)
        elif self.args.serial is not None:
            return "SERIAL", self.args.serial
        else:
            return "TCP", ("192.168.2.113", 5760)

    def register_msp_process(self) -> bool:
        conn_type, link = self._determine_connection_config()
        if not conn_type:
            raise ValueError("Не удалось определить тип подключения")

        try:
            msp_config = {
                "mode": conn_type,
                "link": link,
                "analyzer_flag": self.args.analyzer,
                "log": self.args.logging,
                "output": self.args.sensor_output,
                "name": "MSPManagerProcess",
            }

            msp_process = MSPManagerProcess(**msp_config)

            process_info = ProcessInfo(
                name="msp",
                process=msp_process,
                status=ProcessStatus.NOT_STARTED,
            )
            self._processes["msp"] = process_info
            self._logger.info(
                "MSP процесс зарегистрирован (режим: {mode})".format(
                    mode=conn_type
                )
            )

            return True
        except Exception as e:
            self._logger.error(
                "Ошибка регистрации MSP процесса {err}".format(err=e)
            )
            return False

    def register_nav_process(self) -> bool:
        try:
            nav_config = {
                "grpc_port": int(NavigationConfigGRPC.PORT),
                "enable_logging": NavigationConfigGRPC.LOG_TO_FILE,
                "enable_output": NavigationConfigGRPC.LOG_TO_TERMINAL,
                "max_workers": NavigationConfigGRPC.MAX_WORKERS,
            }

            nav_process = NavigationManagerProcess(**nav_config)

            process_info = ProcessInfo(
                name="navigation",
                process=nav_process,
                status=ProcessStatus.NOT_STARTED,
            )
            self._processes["navigation"] = process_info
            self._logger.info(
                "Navigation процесс зарегистрирован (порт: {port})".format(
                    port=NavigationConfigGRPC.PORT
                )
            )

            return True

        except Exception as e:
            self._logger.error(
                "Ошибка регистрации Navigation процесса {err}".format(err=e)
            )
            return False

    def register_vision_process(self) -> bool:
        try:
            vision_config = {
                "camera_url": VisionConfigGRPC.CAMERA_URL,
                "grpc_port": int(VisionConfigGRPC.PORT),
                "enable_logging": VisionConfigGRPC.LOG_TO_FILE,
                "enable_output": VisionConfigGRPC.LOG_TO_TERMINAL,
                "max_workers": VisionConfigGRPC.MAX_WORKERS,
            }

            vision_process = VisionManagerProcess(**vision_config)

            process_info = ProcessInfo(
                name="vision",
                process=vision_process,
                status=ProcessStatus.NOT_STARTED,
            )
            self._processes["vision"] = process_info
            self._logger.info(
                "Vision процесс зарегистрирован (порт: {port})".format(
                    port=VisionConfigGRPC.PORT
                )
            )

            return True
        except Exception as e:
            self._logger.error(
                "Ошибка регистрации Vision процесса {err}".format(err=e)
            )
            return False

    def register_rest_process(self) -> bool:
        try:
            rest_process = RESTAPIProcess(host="0.0.0.0", port=50054)

            process_info = ProcessInfo(
                name="rest",
                process=rest_process,
                status=ProcessStatus.NOT_STARTED,
            )

            self._processes["rest"] = rest_process
            self._logger.info(
                "REST процесс зарегистрирован (порт: {port})".format(
                    port=50054
                )
            )

            return True
        except Exception as e:
            self._logger.error(
                "Ошибка регистрации REST процесса {err}".format(err=e)
            )
            return False

    def setup_processes(self) -> bool:
        try:
            if not self.register_msp_process():
                self._logger.error("Не удалось зарегистрировать MSP процесс")
                return False

            if not self.args.only_msp:
                if not self.register_nav_process():
                    self._logger.warning(
                        "Не удалось зарегистрировать Navigation процесс"
                    )
                    return False

                if not self.register_vision_process():
                    self._logger.warning(
                        "Не удалось зарегистрировать Vision процесс"
                    )
                    return False
            self._logger.info(
                "Настроено {count} процессов".format(
                    count=len(self._processes)
                )
            )
            return True
        except Exception as e:
            self._logger.error(
                "Ошибка пр инастройке процессов {error}".format(error=e)
            )
            return False

    def start_processes(self) -> bool:
        if not self._processes:
            self._logger.error("Нет зарегистрированных процессов для запуска")
            return False

        self._running = True
        self._stop_event.clear()

        self._setup_signal_handlers()

        if self.dev_mode:
            self._setup_debugger()

        success_count = 0
        for name, process_info in self._processes.items():
            if self._start_single_process(process_info):
                success_count += 1

        if success_count == len(self._processes):
            self._logger.info(
                "Все процессы успешно запущены ({count} процессов)".format(
                    count=len(self._processes)
                )
            )
            return True
        else:
            self._logger.error(
                "Некоторые процессы не удалось запустить "
                "({success}/{total})".format(
                    success=success_count, total=len(self._processes)
                )
            )
            return False

    def _start_single_process(self, process_info: ProcessInfo) -> bool:
        try:
            self._logger.info(
                "Запуск процесса {name}...".format(name=process_info.name)
            )
            process_info.status = ProcessStatus.STARTING
            process_info.start_time = time.time()

            process_info.process.start()

            time.sleep(0.2)  # Небольшая задержка для стабильности

            if process_info.process.is_alive():
                process_info.status = ProcessStatus.RUNNING
                self._logger.info(
                    "Процесс {name} успешно запущен".format(
                        name=process_info.name
                    )
                )
                return True
            else:
                process_info.status = ProcessStatus.ERROR
                process_info.error_message = "Процесс не запустился"
                self._logger.error(
                    "Процесс {name} не запустился".format(
                        name=process_info.name
                    )
                )
                return False

        except Exception as e:
            process_info.status = ProcessStatus.ERROR
            process_info.error_message = str(e)
            self._logger.error(
                "Ошибка при запуске процесса {name}: {error}".format(
                    name=process_info.name, error=e
                )
            )
            return False

    def _setup_debugger(self) -> None:
        try:
            self.debugger = Debugger(debug=self.dev_mode, reload_interval=5.0)

            modules_to_watch = [
                "ara_api._core",
                "ara_api._utils",
                "ara_api._core.services",
                "ara_api._core.processors",
            ]

            for module in modules_to_watch:
                self.debugger.add_module(module)

            self.debugger.set_restart_callback(self._handle_hot_reload)
            self.debugger.start()

            self._logger.info("Дебаггер успешно настроен и запущен")
        except Exception as e:
            self._logger.error(
                "Ошибка при настройке дебаггера: {error}".format(error=e)
            )
            self.debugger = None

    def _handle_hot_reload(self, module_name: str) -> None:
        self._logger.info(
            "Модуль {name} изменен, перезапуск...".format(name=module_name)
        )

        process_to_restart = self._determine_affected_processes(module_name)

        for process_name in process_to_restart:
            if process_name in self._processes:
                self._restart_process(process_name)

    def _determine_affected_processes(self, module_name: str) -> List[str]:
        return list(self._processes.keys())

    def _restart_process(self, process_name: str) -> bool:
        if process_name not in self._processes:
            self._logger.error(
                "Процесс {name} не найден".format(name=process_name)
            )
            return False

        process_info = self._processes[process_name]

        if not self._stop_single_process(process_info):
            self._logger.error(
                "Не удалось остановить процесс {name}".format(
                    name=process_name
                )
            )
            return False

        if not self._recreate_process(process_name):
            self._logger.error(
                "Не удалось пересоздать процесс {name}".format(
                    name=process_name
                )
            )
            return False

        return self._start_single_process(process_info)

    def _recreate_process(self, process_name: str) -> bool:
        if process_name == "msp":
            return self.register_msp_process()
        elif process_name == "navigation":
            return self.register_nav_process()
        elif process_name == "vision":
            return self.register_vision_process()

        self._logger.warning(
            "Неизвестный процесс {name}, не удалось пересоздать".format(
                name=process_name
            )
        )

        return True

    def _setup_signal_handlers(self) -> None:
        def signal_handler(signum, frame):
            try:
                sig_name = signal.Signals(signum).name
                self._logger.info(
                    "Получен сигнал {signal}, остановка процессов...".format(
                        signal=sig_name
                    )
                )
                self.stop_processes()
            except Exception as e:
                self._logger.error(
                    "Ошибка при обработке сигнала {signal}: {error}".format(
                        signal=signum, error=e
                    )
                )
                sys.exit(1)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def monitor_processes(self) -> None:
        self._logger.info("Мониторинг процессов запущен")

        try:
            while self._running and not self._stop_event.is_set():
                terminated_processes = []

                for name, process_info in self._processes.items():
                    if not process_info.process.is_alive():
                        if process_info.status != ProcessStatus.RUNNING:
                            process_info.status = ProcessStatus.ERROR
                            exit_code = getattr(
                                process_info.process, "exitcode", None
                            )
                            self._logger.warning(
                                "Процесс {name} остановлен с "
                                "кодом выхода {exit_code}".format(
                                    name=name, exit_code=exit_code
                                )
                            )
                for name in terminated_processes:
                    del self._processes[name]

                if not self._processes:
                    self._logger.info("Все процессы остановлены")
                    self._running = False
                    break

                time.sleep(0.5)  # Пауза между проверками

        except KeyboardInterrupt:
            self._logger.info("Мониторинг процессов остановлен пользователем")
        except Exception as e:
            self._logger.error(
                "Ошибка в процессе мониторинга: {error}".format(error=e)
            )
        finally:
            self.stop_processes()

    def stop_processes(self) -> None:
        if not self._running:
            return

        self._logger.info("Остановка процессов...")
        self._stop_event.set()
        self._running = False

        if self.debugger:
            try:
                self.debugger.stop()
                self._logger.info("Дебаггер остановлен")
            except Exception as e:
                self._logger.error(
                    "Ошибка при остановке дебаггера: {error}".format(error=e)
                )

        for name, process_info in list(self._processes.items()):
            self._stop_single_process(process_info)

        self._logger.info("Все процессы остановлены")

    def _stop_single_process(self, process_info: ProcessInfo) -> bool:
        self._logger.info(
            "Остановка процесса {name}...".format(name=process_info.name)
        )
        process_info.status = ProcessStatus.STOPPING

        try:
            if process_info.process.is_alive():
                process_info.process.terminate()
                process_info.process.join(timeout=3.0)

                if process_info.process.is_alive():
                    self._logger.warning(
                        "Принудительное завершение процесса {name}".format(
                            name=process_info.name
                        )
                    )
                    process_info.process.kill()
                    process_info.process.join(timeout=1.0)

            process_info.status = ProcessStatus.STOPPED
            self._logger.info(
                "Процесс {name} успешно остановлен".format(
                    name=process_info.name
                )
            )
            return True

        except Exception as e:
            process_info.status = ProcessStatus.ERROR
            process_info.error_message = str(e)
            self._logger.error(
                "Ошибка при остановке процесса {name}: {error}".format(
                    name=process_info.name, error=e
                )
            )
            return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "process_count": len(self._processes),
            "processes": {
                name: {
                    "status": process_info.status.value,
                    "alive": process_info.process.is_alive(),
                    "start_time": process_info.start_time,
                    "error": process_info.error_message,
                }
                for name, process_info in self._processes.items()
            },
            "dev_mode": self.dev_mode,
        }

    def mainloop(self) -> None:
        try:
            if self.args.docs:
                self._ui_helper.show_docs()
                return
            else:
                self._ui_helper.display_header(self.args)

            if not self.setup_processes():
                self._logger.error("Ошибка при настройке процессов")
                sys.exit(1)

            if not self.start_processes():
                self._logger.error("Ошибка при запуске процессов")
                self.stop_processes()
                sys.exit(1)

            self.monitor_processes()
        except Exception as e:
            self._logger.error(
                "Ошибка в основном цикле приложения: {error}".format(error=e)
            )
            self.stop_processes()
            sys.exit(1)

import threading
import time

import grpc

from ara_api._core.services.nav.behavior import (
    NavigationContext,
    NavigationStateMachine,
)
from ara_api._core.services.nav.checker import SimpleGoalChecker
from ara_api._core.services.nav.controller import MPPIController
from ara_api._core.services.nav.planner import GlobalNavigationPlanner
from ara_api._utils import (
    Altitude,
    DroneState,
    Logger,
    NavigationServicer,
    NavigationState,
    Path,
    Rotation,
    Vector3,
    gRPCSync,
    status,
)
from ara_api._utils.config import NavigationConfigGRPC


class NavigationManager(NavigationServicer):
    """Менеджер навигационной системы дрона."""

    def __init__(self, log: bool = True, output: bool = True):
        """Инициализация NavigationManager.

        Args:
            msp_manager: Ссылка на MSP менеджер для взаимодействия
                с полетным контроллером.
            log: Флаг логирования в файл.
            output: Флаг вывода в терминал.
        """
        self._initialized = False
        self._lock = threading.Lock()

        self._logger = Logger(
            log_level=NavigationConfigGRPC.LOG_LEVEL,
            log_to_file=log,
            log_to_terminal=output,
        )

        # Навигационные данные
        self.drone_state = DroneState(
            ID=0,
            IP="",
            PORT="",
            position=Vector3(x=0.0, y=0.0, z=0.0),
            attitude=Rotation(),
            timestamp=time.time(),
            battery_voltage=4.2,  # TODO: add battery voltage handling
            state=NavigationState.IDLE,
            current_path=Path(),
        )

        self._nav_context = NavigationContext(
            state_machine=NavigationStateMachine(
                self._logger, NavigationConfigGRPC.MAX_WORKERS
            ),
            logger=self._logger,
            drone_state=self.drone_state,
            controller=MPPIController(),
            global_planner=GlobalNavigationPlanner(),
            goal_checker=SimpleGoalChecker(),
            grpc_sync=gRPCSync(),
        )

        self._target_altitude = Altitude(0.0)
        self._target_position = Vector3(x=0.0, y=0.0, z=0.0)
        self._target_velocity = Vector3(x=0.0, y=0.0, z=0.0)

        self._logger.debug("NavigationManager инициализирован")

    def initialize(self) -> bool:
        with self._lock:
            if self._initialized:
                self._logger.debug("NavigationManager уже инициализирован")
                return True

            try:
                self._initialized = True
                self._logger.debug("NavigationManager успешно инициализирован")
                return True
            except Exception as e:
                self._logger.error(
                    "Ошибка инициализации NavigationManager: {e}".format(e=e)
                )
                self._initialized = False
                return False

    def cmd_takeoff_rpc(self, request, context) -> status:
        """Команда взлета.

        Args:
            request: Запрос с параметрами взлета.
            context: Контекст gRPC.

        Returns:
            Ответ с результатом выполнения команды взлета.
        """
        try:
            metadata = dict(context.invocation_metadata())

            if not self._initialized:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("NavigationManager не инициализирован")
                self._logger.error(
                    "[TAKEOFF]: cmd_takeoff_rpc вызван, "
                    "но NavigationManager не инициализирован"
                )
                return status(status="NavigationManager не инициализирован")

            self._logger.debug(
                f"[TAKEOFF]: Запрос от клиента: {context.peer()}"
            )
            self._logger.debug(
                "[TAKEOFF]:Команда взлета на высоту {alt}м".format(
                    alt=request.data
                )
            )

            if metadata.get("source") == "test":
                self._logger.warning(
                    "[TAKEOFF]: Запуск тестовой работы сервиса взлета"
                )
                self._logger.debug(
                    "[TAKEOFF]: Команда взлета от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[TAKEOFF]: Metadata: {meta}".format(meta=metadata)
                )

                return status(status="Тест команды взлета успешно выполнена")
            elif metadata.get("source") == "test-cmd":
                self._logger.warning(
                    "[TAKEOFF]: Запуск тестовой работы сервиса по посадке от test-cmd"
                )
                self._logger.debug(
                    "[TAKEOFF]: Команда посадки от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[TAKEOFF]: Metadata: {meta}".format(meta=metadata)
                )

                with self._lock:
                    self._logger.debug("Блокировка процесса для взлета")
                    self._nav_context.state_machine.transition(
                        NavigationState.TAKEOFF,
                        target=request.data,
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )
            else:
                with self._lock:
                    self._nav_context.state_machine.transition(
                        NavigationState.TAKEOFF,
                        target_altitude=request.data,
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )

            return status(status="Команда взлета успешно выполнена")

        except Exception as e:
            self._logger.error(
                f"[TAKEOFF]: Ошибка выполнения команды взлета: {e}"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка взлета: {str(e)}")
            return status(status=f"Ошибка взлета: {str(e)}")

    def cmd_land_rpc(self, request, context) -> status:
        """Команда посадки.

        Args:
            request: Запрос на посадку.
            context: Контекст gRPC.

        Returns:
            Ответ с результатом выполнения команды посадки.
        """
        try:
            metadata = dict(context.invocation_metadata())

            if not self._initialized:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("NavigationManager не инициализирован")
                self._logger.error(
                    "cmd_land_rpc вызван, "
                    "но NavigationManager не инициализирован"
                )
                return status(status="NavigationManager не инициализирован")

            self._logger.debug(f"[LAND]: Запрос от клиента: {context.peer()}")
            self._logger.debug("[LAND]:Команда посадки")

            if metadata.get("source") == "test":
                self._logger.warning(
                    "[LAND]: Запуск тестовой работы сервиса по посадке"
                )
                self._logger.debug(
                    "[LAND]: Команда посадки от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[LAND]: Metadata: {meta}".format(meta=metadata)
                )

                return status(status="Тест команды посадки успешно выполнена")
            elif metadata.get("source") == "test-cmd":
                self._logger.warning(
                    "[LAND]: Запуск тестовой работы сервиса по посадке от test-cmd"
                )
                self._logger.debug(
                    "[LAND]: Команда посадки от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[LAND]: Metadata: {meta}".format(meta=metadata)
                )

                with self._lock:
                    self._logger.debug(
                        "[LAND]: Блокировка процесса для посадки"
                    )
                    self._nav_context.state_machine.transition(
                        NavigationState.LAND,
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )
            else:
                with self._lock:
                    self._nav_context.state_machine.transition(
                        NavigationState.LAND,
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )

            return status(status="Команда посадки успешно выполнена")

        except Exception as e:
            self._logger.error(
                f"[LAND]: Ошибка выполнения команды посадки: {e}"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка посадки: {str(e)}")
            return status(status=f"Ошибка посадки: {str(e)}")

    def cmd_move_rpc(self, request, context) -> status:
        """Команда перемещения в заданную точку."""
        try:
            metadata = dict(context.invocation_metadata())

            if not self._initialized:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("NavigationManager не инициализирован")
                self._logger.error(
                    "cmd_move_rpc вызван, "
                    "но NavigationManager не инициализирован"
                )
                return status(status="NavigationManager не инициализирован")

            self._logger.debug(f"[MOVE]: Запрос от клиента: {context.peer()}")
            coords = f"({request.x}, {request.y}, {request.z})"
            self._logger.debug(f"[MOVE]: Команда перемещения в точку {coords}")

            if metadata.get("source") == "test":
                self._logger.warning(
                    "[MOVE]: Запуск тестовой работы сервиса по перемещению"
                )
                self._logger.debug(
                    "[MOVE]: Команда перемещения по точкам от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[MOVE]: Metadata: {meta}".format(meta=metadata)
                )

                return status(
                    status="Тест команды перемещения успешно выполнен"
                )
            elif metadata.get("source") == "test-cmd":
                self._logger.warning(
                    "[MOVE]: Запуск тестовой работы сервиса по перемещению от test-cmd"
                )
                self._logger.debug(
                    "[MOVE]: Команда перемещения от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[MOVE]: Metadata: {meta}".format(meta=metadata)
                )

                with self._lock:
                    self._logger.debug("[MOVE]: Блокировка процесса для точек")
                    self._nav_context.state_machine.transition(
                        NavigationState.MOVE,
                        target_position=self._target_position,
                        state=self._nav_context.drone_state,
                        nav_context=self._nav_context,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )
            else:
                with self._lock:
                    self._target_position = Vector3(
                        x=request.x, y=request.y, z=request.z
                    )
                    self._nav_context.state_machine.transition(
                        NavigationState.MOVE,
                        target_position=self._target_position,
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )

            return status(status="Команда перемещения успешно выполнена")

        except Exception as e:
            self._logger.error(
                f"[MOVE]: Ошибка выполнения команды перемещения: {e}"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка перемещения: {str(e)}")
            return status(status=f"Ошибка перемещения: {str(e)}")

    def cmd_velocity_rpc(self, request, context) -> status:
        """Команда управления скоростью.

        Args:
            request: Запрос с компонентами скорости.
            context: Контекст gRPC.

        Returns:
            Ответ с результатом выполнения команды скорости.
        """
        try:
            metadata = dict(context.invocation_metadata())

            if not self._initialized:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("NavigationManager не инициализирован")
                self._logger.error(
                    "cmd_velocity_rpc вызван, "
                    "но NavigationManager не инициализирован"
                )
                return status(status="NavigationManager не инициализирован")

            self._logger.debug(f"[SPEED]: Запрос от клиента: {context.peer()}")
            velocities = f"vx={request.x}, vy={request.y}"
            self._logger.debug(f"[SPEED]: Команда скорости: {velocities}")

            if metadata.get("source") == "test":
                self._logger.warning(
                    "[SPEED]: Запуск тестовой работы сервиса по управлению скоростью"
                )
                self._logger.debug(
                    "[SPEED]: Команда изменения скорости от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[SPEED]: Metadata: {meta}".format(meta=metadata)
                )

                return status(
                    status="Тест команды управления скоростью успешно выполнен"
                )
            elif metadata.get("source") == "test-cmd":
                self._logger.warning(
                    "[SPEED]: Запуск тестовой работы сервиса по скорости от test-cmd"
                )
                self._logger.debug(
                    "[SPEED]: Команда скорости от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug("Metadata: {meta}".format(meta=metadata))

                with self._lock:
                    self._logger.debug(
                        "[SPEED]: Блокировка процесса для скорости"
                    )
                    self._nav_context.state_machine.transition(
                        NavigationState.SPEED,
                        target_velocity=(request.x, request.y),
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )
            else:
                with self._lock:
                    self._nav_context.state_machine.transition(
                        NavigationState.SPEED,
                        target_velocity=(request.x, request.y),
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )

            return status(status="Команда скорости успешно выполнена")

        except Exception as e:
            self._logger.error(
                f"[SPEED]: Ошибка выполнения команды скорости: {e}"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка установки скорости: {str(e)}")
            return status(status=f"Ошибка установки скорости: {str(e)}")

    def cmd_altitude_rpc(self, request, context) -> status:
        """Команда изменения высоты.

        Args:
            request: Запрос с целевой высотой.
            context: Контекст gRPC.

        Returns:
            Ответ с результатом выполнения команды изменения высоты.
        """
        try:
            metadata = dict(context.invocation_metadata())

            if not self._initialized:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("NavigationManager не инициализирован")
                self._logger.error(
                    "cmd_altitude_rpc вызван, "
                    "но NavigationManager не инициализирован"
                )
                return status(status="NavigationManager не инициализирован")

            self._logger.debug(
                f"[ALTITUDE]: Запрос от клиента: {context.peer()}"
            )
            self._logger.debug(
                f"[ALTITUDE]: Команда изменения высоты на {request.data}м"
            )

            if metadata.get("source") == "test":
                self._logger.warning(
                    "[ALTITUDE]: Запуск тестовой работы сервиса по изменению высоты"
                )
                self._logger.debug(
                    "[ALTITUDE]: Команда изменения высоты от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[ALTITUDE]: Metadata: {meta}".format(meta=metadata)
                )

                return status(
                    status="Тест команды изменения высоты успешно выполнен"
                )
            elif metadata.get("source") == "test-cmd":
                self._logger.warning(
                    "[ALTITUDE]: Запуск тестовой работы сервиса по высоте от test-cmd"
                )
                self._logger.debug(
                    "[ALTITUDE]: Команда высоты от источника: {src}".format(
                        src=metadata["source"]
                    )
                )
                self._logger.debug(
                    "[ALTITUDE]: Metadata: {meta}".format(meta=metadata)
                )

                with self._lock:
                    self._logger.debug(
                        "[ALTITUDE]: Блокировка процесса для высоты"
                    )
                    self._nav_context.state_machine.transition(
                        NavigationState.ALTITUDE,
                        target_altitude=self._target_altitude,
                        state=self._nav_context.drone_state,
                        source=metadata["source"]
                        if "source" in metadata
                        else "default",
                    )
            else:
                with self._lock:
                    self._target_altitude = Altitude(request.altitude)
                    self._nav_context.drone_state = (
                        self._nav_context.state_machine.transition(
                            NavigationState.ALTITUDE,
                            target_altitude=self._target_altitude,
                            state=self._nav_context.drone_state,
                            source=metadata["source"]
                            if "source" in metadata
                            else "default",
                        )
                    )

            return status(status="Команда изменения высоты успешно выполнена")

        except Exception as e:
            self._logger.error(
                f"[ALTITUDE]: Ошибка выполнения команды высоты: {e}"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка установки высоты: {str(e)}")
            return status(status=f"Ошибка установки высоты: {str(e)}")

    def update(self) -> None:
        """Обновление состояния навигационной системы.

        Синхронизирует данные с MSP менеджером и обновляет
        внутреннее состояние навигационной системы.
        """
        pass


if __name__ == "__main__":
    import asyncio
    from concurrent import futures

    import grpc

    from ara_api._utils import add_navigation_to_server

    async def serve():
        nav_manager = NavigationManager(log=True, output=True)

        if not nav_manager.initialize():
            print("Failed to initialize NavigationManager")
            return

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

        add_navigation_to_server(nav_manager, server)

        listen_address = f"[::]:{NavigationConfigGRPC.PORT}"
        server.add_insecure_port(listen_address)

        print(f"Starting gRPC server on {listen_address}")
        server.start()

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            print("Server stopped by user")
            server.stop(0)

    asyncio.run(serve())

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ara_api._core.services.nav.behavior.command_processor import (
        NavigationCommandProcessor,
    )
    from ara_api._core.services.nav.behavior.nav_state_machine import (
        NavigationStateMachine,
    )
    from ara_api._core.services.nav.checker import SimpleGoalChecker
    from ara_api._core.services.nav.controller import MPPIController
    from ara_api._core.services.nav.planner import GlobalNavigationPlanner
    from ara_api._utils import Logger, gRPCSync
    from ara_api._utils.data import DroneState


@dataclass
class NavigationContext:
    """Контекст навигационной системы."""

    # Основные компоненты
    state_machine: "NavigationStateMachine"
    logger: "Logger"

    # Данные дрона
    drone_state: "DroneState"

    # Навигационные компоненты
    controller: "MPPIController"
    global_planner: "GlobalNavigationPlanner"
    goal_checker: "SimpleGoalChecker"

    # Интеграция с другими системами
    grpc_sync: "gRPCSync"

from enum import Enum


class NavigationState(Enum):
    """Navigation system state enumeration."""

    IDLE = "IDLE"
    FLYING = "FLYING"
    EMERGENCY = "EMERGENCY"
    TAKEOFF = "TAKEOFF"
    MOVE = "MOVE"
    SPEED = "SPEED"
    LAND = "LAND"
    ALTITUDE = "ALTITUDE"


class FlightMode(Enum):
    """Flight mode enumeration."""

    STABILIZE = "STABILIZE"
    ALTITUDE_HOLD = "ALTITUDE_HOLD"
    POSITION_HOLD = "POSITION_HOLD"


class PlanningAlgorithm(Enum):
    """Доступные алгоритмы глобального планирования."""

    A_STAR = "A*"
    RRT_STAR = "RRT*"
    CARROT = "Carrot"

"""
Core components and interfaces for the ARA API system.

This package provides fundamental abstractions, interfaces, and error
handling mechanisms that form the foundation of the ARA API
architecture. It defines the base classes and contracts that the rest
of the system builds upon.

Components:
    - interfaces: Abstract base classes defining component contracts
    - exception: Comprehensive exception hierarchy for error handling

The _core package should be kept minimal and focused on elements
essential to the system's architecture. Implementation details belong
in dedicated modules.
"""

from ara_api._core.manager import ApplicationManager
from ara_api._core.processors import (
    MSPManagerProcess,
    NavigationManagerProcess,
    VisionManagerProcess,
)
from ara_api._core.services import (
    # Planners
    GlobalNavigationPlanner,
    # Codes
    MSPCodes,
    # Controllers
    MSPController,
    # Managers
    MSPManager,
    NavigationManager,
    VisionController,
    VisionManager,
    # Entry points
    # analyzer_entry_point,
)

__all__ = [
    # Processors
    "MSPManagerProcess",
    "NavigationManagerProcess",
    "VisionManagerProcess",
    # Manager
    "MSPManager",
    "NavigationManager",
    "VisionManager",
    # Controllers
    "MSPController",
    "VisionController",
    # Planners
    "GlobalNavigationPlanner",
    # Codes
    "MSPCodes",
    # Entry points
    # "analyzer_entry_point",
    # Application Manager
    "ApplicationManager",
]

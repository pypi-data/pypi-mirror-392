import importlib
import os
import sys
import threading
import time
import traceback
from types import ModuleType
from typing import Callable, Dict, List, Optional, Set, Union

from ara_api._utils.logger import Logger


class Debugger:
    def __init__(
        self,
        debug: bool = False,
        reload_interval: float = 1.0,
        log: bool = False,
        output: bool = False,
    ):
        """
        Initialize a debugger with hot-reloading capability.

        Args:
            debug: Whether debugging is enabled
            reload_interval: How often to check for module changes
                             (in seconds)
        """
        self.debug = debug
        # Logger will be set externally
        self.logger = Logger(log_to_file=log, log_to_terminal=output)
        self.reload_interval = reload_interval
        self._modules_to_watch: Dict[
            str, float
        ] = {}  # module name -> last modified time
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        self._restart_callback = None
        self._ignore_modules: Set[str] = {
            "sys",
            "os",
            "threading",
            "importlib",
            "time",
            "__main__",
            "__builtin__",
            "builtins",
        }

        # Verbose mode for debugging the debugger
        self._verbose = True

    @property
    def name(self) -> str:
        """Return the name of this debugger."""
        return "module_reloader"

    def start(
        self, modules: Optional[List[Union[str, ModuleType]]] = None
    ) -> None:
        """
        Start the module reloader thread.

        Args:
            modules: Optional list of modules to watch
        """
        if not self.debug:
            return

        if self._running:
            self.log("Module reloader already running")
            return

        self._running = True
        self._stop_event.clear()

        # Add modules to watch if specified
        if modules:
            for module in modules:
                self.add_module(module)

        self.log(
            f"Module reloader started. Monitoring "
            f"{len(self._modules_to_watch)} modules"
        )
        self._print_watched_modules()

        # Start monitoring thread
        self._monitor_thread = threading.Thread(
            target=self._monitor_modules, name="ModuleReloader", daemon=True
        )
        self._monitor_thread.start()

    def stop(self) -> None:
        """Stop the module reloader thread."""
        if not self._running:
            return

        self.log("Module reloader stopped")
        self._stop_event.set()
        self._running = False

        # Wait for thread to terminate
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)

    def set_restart_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set a callback function to be called when modules change.

        Args:
            callback: Function that takes module_name as parameter
        """
        self.log(f"Setting restart callback: {callback.__name__}")
        self._restart_callback = callback

    def _should_monitor_module(self, module_name: str) -> bool:
        """
        Determine if a module should be monitored.

        Args:
            module_name: Name of the module

        Returns:
            True if module should be monitored, False otherwise
        """
        # Skip modules in ignore list
        if module_name in self._ignore_modules:
            return False

        # Skip standard library modules
        if not module_name.startswith("ara_api"):
            return False

        return True

    def add_module(self, module: Union[str, ModuleType]) -> None:
        """
        Add a module to be watched for changes.

        Args:
            module: Either a module object or name
        """
        if not self.debug:
            return

        try:
            # Convert string to module if necessary
            if isinstance(module, str):
                # Try to import the module
                try:
                    imported_module = importlib.import_module(module)
                    module = imported_module
                    self.log(f"Successfully imported module: {module}")
                except ImportError:
                    self.log_warning(f"Failed to import module: {module}")
                    return

            if not isinstance(module, ModuleType):
                self.log_warning(f"Not a module: {module}")
                return

            self._add_module_to_watch(module)

        except Exception as e:
            self.log_warning(f"Error adding module {module}: {e}")
            if self._verbose:
                self.log_warning(traceback.format_exc())

    def _add_module_to_watch(self, module: ModuleType) -> None:
        """
        Add a module to watch list with its last modified time.

        Args:
            module: Module to watch
        """
        module_name = module.__name__

        # Skip modules we shouldn't monitor
        if not self._should_monitor_module(module_name):
            self.log(f"Skipping module: {module_name} (in ignore list)")
            return

        # Get module file path
        if not hasattr(module, "__file__") or not module.__file__:
            self.log_warning(f"Module has no file: {module_name}")
            return

        file_path = module.__file__

        # Convert .pyc to .py
        if file_path.endswith(".pyc"):
            file_path = file_path[:-1]

        # Make sure file exists
        if not os.path.exists(file_path):
            self.log_warning(f"Module file doesn't exist: {file_path}")
            return

        # Get last modified time
        mtime = os.path.getmtime(file_path)

        # Add to watch list
        self._modules_to_watch[module_name] = mtime
        self.log(f"Now watching module: {module_name} ({file_path})")

    def _monitor_modules(self) -> None:
        """
        Monitor modules for changes and reload them when necessary.
        """
        self.log("Module monitoring thread started")

        while not self._stop_event.is_set():
            try:
                # Check each watched module
                for module_name, last_mtime in list(
                    self._modules_to_watch.items()
                ):
                    try:
                        # Check if module is loaded
                        if module_name not in sys.modules:
                            self.log_warning(
                                f"Module no longer loaded: {module_name}"
                            )
                            del self._modules_to_watch[module_name]
                            continue

                        # Get module
                        module = sys.modules[module_name]

                        # Check if module has a file
                        if (
                            not hasattr(module, "__file__")
                            or not module.__file__
                        ):
                            continue

                        # Get file path
                        file_path = module.__file__

                        # Convert .pyc to .py
                        if file_path.endswith(".pyc") or file_path.endswith(
                            ".pyo"
                        ):
                            file_path = file_path[:-1]

                        # Check if file exists
                        if not os.path.exists(file_path):
                            self.log_warning(
                                f"Module file no longer exists: {file_path}"
                            )
                            continue

                        # Get current modified time
                        current_mtime = os.path.getmtime(file_path)

                        # Check if file has been modified
                        if current_mtime > last_mtime:
                            self.log(
                                f"Module changed: {module_name} ({file_path})"
                            )
                            self.log(
                                f"Last mtime: {last_mtime},"
                                f"Current mtime: {current_mtime}"
                            )

                            # Reload module
                            try:
                                importlib.reload(module)
                                self.log(
                                    f"Successfully reloaded module: "
                                    f"{module_name}"
                                )

                                # Update last modified time
                                self._modules_to_watch[module_name] = (
                                    current_mtime
                                )

                                # Call restart callback if set
                                if self._restart_callback:
                                    self.log(
                                        f"Calling restart callback for module:"
                                        f" {module_name}"
                                    )
                                    self._restart_callback(module_name)
                            except Exception as e:
                                self.log_warning(
                                    f"Error reloading module {module_name}:"
                                    f" {e}"
                                )
                                if self._verbose:
                                    self.log_warning(traceback.format_exc())
                    except Exception as e:
                        self.log_warning(
                            f"Error checking module {module_name}: {e}"
                        )

                # Sleep for a bit
                self._stop_event.wait(self.reload_interval)
            except Exception as e:
                self.log_warning(f"Error in monitoring thread: {e}")
                if self._verbose:
                    self.log_warning(traceback.format_exc())
                time.sleep(1)  # Avoid tight loop if there's a persistent error

    def ignore_module(self, module_name: str) -> None:
        """
        Add a module to the ignore list.

        Args:
            module_name: Name of module to ignore
        """
        self._ignore_modules.add(module_name)

        # Remove from watch list if present
        if module_name in self._modules_to_watch:
            del self._modules_to_watch[module_name]

    def _print_watched_modules(self) -> None:
        """Print the list of modules being watched."""
        if not self._modules_to_watch:
            self.log("No modules being watched")
            return

        self.log("Currently watching modules:")
        for module_name, mtime in self._modules_to_watch.items():
            if module_name in sys.modules and hasattr(
                sys.modules[module_name], "__file__"
            ):
                file_path = sys.modules[module_name].__file__ or "unknown"
                self.log(f"  {module_name}: {file_path} (mtime: {mtime})")
            else:
                self.log(f"  {module_name}: unknown file (mtime: {mtime})")

    # Helper methods for logging
    def log(self, message: str) -> None:
        """Log an info message."""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"[DEBUG] {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        if self.logger:
            self.logger.warning(message)
        else:
            print(f"[DEBUG WARNING] {message}")

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass
class CommandResult:
    """Результат выполнения навигационной команды.

    Attributes:
        success: Флаг успешного выполнения команды.
        message: Сообщение о результате выполнения.
        data: Дополнительные данные результата.
    """

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class NavigationCommand(Protocol):
    """Протокол для навигационных команд.

    Все навигационные команды должны реализовывать этот интерфейс.
    """

    def can_execute(self, *args, **kwargs) -> bool:
        """Проверяет возможность выполнения команды.

        Returns:
            True если команда может быть выполнена, False иначе.
        """
        ...

    def execute(self, *args, **kwargs) -> CommandResult:
        """Выполняет навигационную команду.

        Returns:
            Результат выполнения команды.
        """
        ...

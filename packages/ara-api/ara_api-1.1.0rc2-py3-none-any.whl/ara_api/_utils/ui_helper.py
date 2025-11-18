import argparse
from importlib.metadata import version
from typing import Optional, Tuple, Union

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class UIHelper:
    """Помощник для отображения UI в терминале.

    Использует rich для создания структурированного вывода
    информации о ARA API.
    """

    def __init__(self) -> None:
        """Инициализация UIHelper с настройкой консоли."""
        # Создаем консоль
        self.console = Console()
        self._api_version = version("ara_api")

        # Получаем размер терминала для адаптивной верстки
        self.terminal_size = self.console.size
        self.terminal_width = self.terminal_size.width
        self.terminal_height = self.terminal_size.height

    def _update_terminal_size(self) -> None:
        """Обновляет размер терминала для адаптивной верстки."""
        self.terminal_size = self.console.size
        self.terminal_width = self.terminal_size.width
        self.terminal_height = self.terminal_size.height

    def _get_adaptive_column_width(self, percentage: float) -> int:
        """Вычисляет ширину колонки в процентах от ширины терминала.

        Args:
            percentage: Процент от ширины терминала (0.0 - 1.0)

        Returns:
            Ширина колонки в символах
        """
        # Учитываем отступы и границы панели (примерно 6 символов)
        available_width = max(self.terminal_width - 6, 60)  # Минимум 60
        return int(available_width * percentage)

    def _get_adaptive_table_widths(self) -> Tuple[int, int, int]:
        """Вычисляет адаптивные ширины для трехколоночных таблиц.

        Returns:
            Кортеж из трех ширин колонок
        """
        if self.terminal_width < 80:
            # Для узких терминалов
            return (15, 25, 25)
        elif self.terminal_width < 120:
            # Для средних терминалов
            return (20, 30, 35)
        else:
            # Для широких терминалов
            return (25, 35, 45)

    def _create_logo(self) -> Text:
        """Создает ASCII logo для ARA API.

        Returns:
            Text: ASCII logo с форматированием
        """
        logo = """
        ██
      ██ █ ███
     █ ███████
      █  ██  █
      █ ████
     █  █████
     █  ████
    ███ ███
        """
        logo_text = Text(logo, style="bold cyan")
        return logo_text

    def _create_services_list(self, args: argparse.Namespace) -> Table:
        """Создает список сервисов с их статусами.

        Args:
            args: Аргументы командной строки

        Returns:
            Table: Таблица с информацией о сервисах
        """
        services_table = Table(
            show_header=True,
            header_style="bold cyan",
            show_edge=False,
            pad_edge=False,
        )

        services_table.add_column("Service", style="bold magenta")
        services_table.add_column("Description", style="white")
        services_table.add_column("Status", style="yellow")

        conn_type, link = self._determine_connection_config(args)
        if conn_type == "TCP":
            msp_path = f"TCP: {link[0]}:{link[1]}"
        else:
            msp_path = f"Serial: {link}"

        services_table.add_row(
            "MSP Service",
            "Flight controller communication",
            f"[green]Starting[/green]\n{msp_path}",
        )

        if not args.only_msp:
            services_table.add_row(
                "Navigation Service",
                "Autonomous flight control",
                "[green]Starting[/green]\ngRPC: localhost:50051",
            )

            services_table.add_row(
                "Vision Service",
                "Computer vision processing",
                "[green]Starting[/green]\ngRPC: localhost:50052",
            )

            services_table.add_row(
                "REST API",
                "Web interface",
                "[green]Starting[/green]\nHTTP: 0.0.0.0:50054",
            )

        return services_table

    def _determine_connection_config(
        self, args: argparse.Namespace
    ) -> Tuple[str, Union[Tuple[str, int], str]]:
        """Определяет конфигурацию подключения на основе аргументов.

        Args:
            args: Аргументы командной строки

        Returns:
            Tuple: (тип подключения, параметры)
        """
        if args.ip is not None:
            return "TCP", (args.ip, 5760)
        elif args.serial is not None:
            return "SERIAL", args.serial
        else:
            return "TCP", ("192.168.2.113", 5760)

    def _create_header(self) -> Panel:
        """Создает заголовок с названием API и версией.

        Returns:
            Panel: Панель с заголовком приложения.
        """
        header_text = Text()
        header_text.append("ARA MINI API", style="bold blue")
        header_text.append(f" v{self._api_version}", style="dim blue")

        return Panel(
            Align.center(header_text),
            style="bright_blue",
            padding=(1, 2),
        )

    def _create_welcome_message(self) -> Panel:
        """Создает приветственное сообщение.

        Returns:
            Panel: Панель с приветствием.
        """
        welcome_text = Text()
        welcome_text.append(
            "[bold green]Добро пожаловать[/bold green] Поздравляем! ",
            style="bold green",
        )
        welcome_text.append(
            "Вы запустили API для программирования ARA MINI", style="cyan"
        )

        return Panel(
            welcome_text,
            style="green",
            padding=(1, 2),
        )

    def _create_connection_info(self) -> Panel:
        """Создает таблицу с информацией о подключении.

        Returns:
            Panel: Панель с таблицей подключений.
        """
        # Обновляем размер терминала
        self._update_terminal_size()

        # Получаем адаптивные ширины колонок
        col1_width, col2_width, col3_width = self._get_adaptive_table_widths()

        connection_table = Table(show_header=True, header_style="bold magenta")
        connection_table.add_column(
            "Тип подключения", style="cyan", width=col1_width
        )
        connection_table.add_column(
            "Адрес", style="bright_magenta", width=col2_width
        )
        connection_table.add_column(
            "Описание", style="white", width=col3_width
        )

        connection_table.add_row(
            "UDP",
            "http://192.168.2.113:14550",
            "Подключение к квадрокоптеру через UDP",
        )
        connection_table.add_row(
            "TCP",
            "http://192.168.2.113:5760",
            "Подключение к квадрокоптеру через TCP",
        )
        connection_table.add_row(
            "Видеопоток",
            "http://192.168.2.113:81/stream",
            "Изображение с камеры дрона",
        )

        return Panel(
            connection_table,
            title="[bold magenta]Подключения[/bold magenta]",
            style="magenta",
            padding=(1, 2),
        )

    def _create_status_info(self, args: argparse.Namespace) -> Optional[Panel]:
        """Создает панель с информацией о статусе.

        Args:
            args: Аргументы командной строки.

        Returns:
            Optional[Panel]: Панель со статусом.
        """
        status_items = []

        if args.sensor_output:
            status_items.append(
                Text("Вывод данных с датчиков включен", style="bold red")
            )

        if args.logging:
            status_items.append(
                Text("Логирование включено", style="bold yellow")
            )

        if args.analyzer:
            status_items.append(
                Text("Режим анализатора активен", style="bold blue")
            )

        if args.only_msp:
            status_items.append(
                Text("Запуск только MSP сервиса", style="bold orange3")
            )

        if status_items:
            status_content = Text()
            for i, item in enumerate(status_items):
                if i > 0:
                    status_content.append("\n")
                status_content.append_text(item)

            return Panel(
                status_content,
                title="[bold red]Статус[/bold red]",
                style="red",
                padding=(1, 2),
            )

        return None

    def _create_project_description(self) -> Panel:
        """Создает описание проекта.

        Returns:
            Panel: Панель с описанием проекта.
        """
        description_text = Text()
        description_text.append(
            "Applied Robotics Avia API ", style="bold magenta"
        )
        description_text.append(
            "— современный высокопроизводительный API для управления дронами ",
            style="cyan",
        )
        description_text.append(
            "ARA MINI, ARA EDU и ARA FPV", style="bold magenta"
        )
        description_text.append(
            ". Использует архитектуру на основе gRPC и MSP "
            "протокола для обеспечения ",
            style="cyan",
        )
        description_text.append(
            "быстрого и надежного взаимодействия с полетным контроллером.",
            style="cyan",
        )

        return Panel(
            description_text,
            title="[bold magenta]О проекте[/bold magenta]",
            style="magenta",
            padding=(1, 2),
        )

    def _create_features_list(self) -> Panel:
        """Создает список основных особенностей.

        Returns:
            Panel: Панель со списком особенностей.
        """
        features_text = Text()
        features = [
            "ARALinkManager - интерфейс для управления дроном",
            "ARAVisionManager - система компьютерного зрения для "
            "анализа изображений",
            "Поддержка MSP протокола для связи с полетным контроллером",
            "Архитектура на основе gRPC для высокой производительности",
            "Встроенный анализатор для отладки и мониторинга",
            "Поддержка TCP и Serial подключений",
            "Автоматическое управление жизненным циклом процессов",
            "Интегрированная система логирования и отладки",
        ]

        for i, feature in enumerate(features, 1):
            features_text.append(f"{i}. ", style="bold blue")
            features_text.append(f"{feature}", style="cyan")
            if i < len(features):
                features_text.append("\n")

        return Panel(
            features_text,
            title="[bold blue]Основные особенности[/bold blue]",
            style="blue",
            padding=(1, 2),
        )

    def _create_libraries_table(self) -> Panel:
        """Создает таблицу с информацией о библиотеках.

        Returns:
            Panel: Панель с таблицей библиотек.
        """
        # Обновляем размер терминала
        self._update_terminal_size()

        # Получаем адаптивные ширины колонок
        col1_width, col2_width, col3_width = self._get_adaptive_table_widths()

        libraries_table = Table(show_header=True, header_style="bold green")
        libraries_table.add_column(
            "Библиотека", style="bright_magenta", width=col1_width
        )
        libraries_table.add_column(
            "Импорт", style="bright_cyan", width=col2_width
        )
        libraries_table.add_column("Описание", style="white", width=col3_width)

        libraries_table.add_row(
            "ARALinkManager",
            "from ara_api.ara_core import ARALinkManager",
            "Управление дроном: взлет, посадка, движение, телеметрия",
        )
        libraries_table.add_row(
            "ARAVisionManager",
            "from ara_api.ara_vision import ARAVisionManager",
            "Компьютерное зрение: ArUco, QR-коды, детекция цветов",
        )

        return Panel(
            libraries_table,
            title="[bold green]Основные библиотеки[/bold green]",
            style="green",
            padding=(1, 2),
        )

    def _create_commands_table(self) -> Panel:
        """Создает таблицу с командами.

        Returns:
            Panel: Панель с таблицей команд.
        """
        # Обновляем размер терминала
        self._update_terminal_size()

        # Для двухколоночной таблицы команд используем другие пропорции
        if self.terminal_width < 80:
            cmd_width = 20
            desc_width = 35
        elif self.terminal_width < 120:
            cmd_width = 25
            desc_width = 50
        else:
            cmd_width = 30
            desc_width = 60

        commands_table = Table(show_header=True, header_style="bold green")
        commands_table.add_column(
            "Команда", style="bright_magenta", width=cmd_width
        )
        commands_table.add_column("Описание", style="white", width=desc_width)

        commands_table.add_row(
            "ara-api-core", "Запуск основного API для управления дроном"
        )
        commands_table.add_row(
            "ara-api-analyzer", "Запуск анализатора для мониторинга данных"
        )
        commands_table.add_row(
            "ara-api-vision", "Запуск vision-сервиса для обработки видео"
        )

        return Panel(
            commands_table,
            title="[bold green]Доступные команды[/bold green]",
            style="green",
            padding=(1, 2),
        )

    def _create_example1_panel(self) -> Panel:
        """Создает панель с первым примером - простое использование.

        Returns:
            Panel: Панель с первым примером кода.
        """
        from rich.syntax import Syntax

        # Обновляем размер терминала
        self._update_terminal_size()

        example1_code = """from ara_api.ara_core import ARALinkManager
import time

manager = ARALinkManager()  # создаём объект для управления квадрокоптером

def main():
    manager.takeoff(1.5)  # взлетаем на высоту 1.5 метра
    time.sleep(5)  # ждём 5 секунд
    manager.move_by_point(1, 0)  # движемся в точку (1,0)
    time.sleep(2)  # ждём 2 секунды для стабилизации
    manager.move_by_point(1, 1)  # движемся в точку (1,1)
    time.sleep(2)  # ждём 2 секунды для стабилизации
    manager.move_by_point(0, 1)  # движемся в точку (0,1)
    time.sleep(2)  # ждём 2 секунды для стабилизации
    manager.move_by_point(0, 0)  # движемся в точку (0,0)
    time.sleep(2)  # ждём 2 секунды для стабилизации
    manager.land()  # приземляемся

if __name__ == "__main__":
    main()"""

        # Адаптируем панель к размеру терминала
        panel_width = max(self.terminal_width - 4, 60)  # Минимум 60 символов

        return Panel(
            Syntax(
                example1_code,
                "python",
                theme="monokai",
                line_numbers=False,
                word_wrap=True,
            ),
            title="[bold green]Пример простого использования[/bold green]",
            style="green",
            padding=(1, 2),
            width=panel_width,
        )

    def _create_example2_panel(self) -> Panel:
        """Создает панель со вторым примером - обнаружение маркеров.

        Returns:
            Panel: Панель со вторым примером кода.
        """
        from rich.syntax import Syntax

        # Обновляем размер терминала
        self._update_terminal_size()

        example2_code = '''from ara_api.ara_core import ARALinkManager
from ara_api.ara_vision import ARAVisionManager
from threading import Thread
import time

manager = ARALinkManager()  # создаём объект для управления квадрокоптером
vision = ARAVisionManager()  # создаём объект для работы с камерой

def read_aruco_data_in_flight():
    """
    Функция для чтения данных с камеры в полёте.
    """
    while True:
        aruco_data = vision.get_aruco_data()  # получаем данные о маркерах
        if aruco_data:
            print("Aruco data:", aruco_data)
        time.sleep(0.5)  # ждём 0.5 секунды перед следующим запросом

def main():
    aruco_thread = Thread(target=read_aruco_data_in_flight, daemon=True)
    aruco_thread.start()  # запускаем поток для камеры

    manager.takeoff(1.5)  # взлетаем на 1.5 метра
    time.sleep(5)  # ждём 5 секунд
    manager.set_velocity(1.5, 0)  # летим вперёд со скоростью 1.5 м/с
    time.sleep(2)  # движение 2 секунды
    manager.set_velocity(-0.5, 0)  # замедляемся
    time.sleep(2)  # пауза 2 секунды
    manager.set_velocity(0, -1.5)  # летим влево со скоростью 1.5 м/с
    time.sleep(4)  # движение 4 секунды
    manager.set_velocity(0, 0.5)  # замедляемся
    time.sleep(2)  # пауза 2 секунды
    manager.land()  # приземляемся

    print(vision.get_aruco_data())  # выводим финальные данные с камеры

if __name__ == "__main__":
    main()'''

        # Адаптируем панель к размеру терминала
        panel_width = max(self.terminal_width - 4, 60)  # Минимум 60 символов

        return Panel(
            Syntax(
                example2_code,
                "python",
                theme="monokai",
                line_numbers=False,
                word_wrap=True,
            ),
            title="[bold green]Пример обнаружения маркеров Aruco[/bold green]",
            style="green",
            padding=(1, 2),
            width=panel_width,
        )

    def display_header(self, args: argparse.Namespace) -> None:
        """Отображает заголовок приложения с информацией.

        Args:
            args: Аргументы командной строки.
        """
        import os

        self._update_terminal_size()
        self.console.clear()

        logo = self._create_logo()

        services = []
        services.append("MSP")
        if not args.only_msp:
            services.extend(["NAV", "VISION", "REST"])

        info_text = Text()
        info_text.append("\n\n")
        info_text.append("ARA API CORE", style="bold cyan")
        info_text.append(f" v{self._api_version}\n", style="cyan")
        info_text.append("Service: ", style="white")
        info_text.append(" ".join(services), style="bold magenta")
        info_text.append("\n")
        info_text.append("Path: ", style="white")
        info_text.append(os.getcwd(), style="dim white")

        layout_table = Table.grid(padding=(0, 1))
        layout_table.add_column(width=15, justify="left")
        layout_table.add_column(width=1, style="dim cyan")
        layout_table.add_column(justify="left")

        layout_table.add_row(logo, "", info_text)

        main_panel = Panel(
            layout_table,
            border_style="cyan",
            padding=(1, 2),
        )

        self.console.print(main_panel)
        self.console.print()

    def show_docs(self) -> None:
        """Отображает полную документацию API."""
        # Обновляем размер терминала при каждом отображении
        self._update_terminal_size()

        self.console.clear()

        # Заголовок
        self.console.print(self.display_header())
        self.console.print()

        # Описание проекта
        self.console.print(self._create_project_description())
        self.console.print()

        # Особенности
        self.console.print(self._create_features_list())
        self.console.print()

        # Библиотеки
        self.console.print(self._create_libraries_table())
        self.console.print()

        # Команды
        self.console.print(self._create_commands_table())
        self.console.print()

        # Примеры
        self.console.print(self._create_example1_panel())
        self.console.print()
        self.console.print(self._create_example2_panel())
        self.console.print()

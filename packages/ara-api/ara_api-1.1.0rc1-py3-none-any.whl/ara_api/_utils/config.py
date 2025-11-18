from typing import Tuple

import numpy as np

from ara_api._utils.enums import PlanningAlgorithm

# =====================================================================
# LOGGER CONFIGURATION
# =====================================================================


class LOGGER_CONFIG:
    LOG_LEVEL: str = "INFO"  # Уровень логирования
    LOG_TO_FILE: bool = False  # Логировать ли в файл
    LOG_TO_TERMINAL: bool = True  # Логировать ли в терминал
    LOG_DIR: str = "logs"  # Директория для логов


# =====================================================================
# gRPC CONFIGURATION
# =====================================================================


class MSPConfigGRPC:
    HOST: str = "localhost"  # Адрес gRPC сервера
    PORT: str = "50051"  # Порт gRPC сервера

    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL


class NavigationConfigGRPC:
    HOST: str = "localhost"  # Адрес gRPC сервера навигации
    PORT: str = "50052"  # Порт gRPC сервера навигации

    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL

    MAX_WORKERS = 4  # Максимальное количество потоков для машины состояний


class VisionConfigGRPC:
    HOST: str = "localhost"  # Адрес gRPC сервера визуализации
    PORT: str = "50053"  # Порт gRPC сервера визуализации

    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL

    CAMERA_URL: str = "http://192.168.2.113:81/stream"  # URL камеры
    # CAMERA_URL: str = "0"  # URL камеры

    MAX_WORKERS = 4  # Максимальное количество потоков


# =====================================================================
# DATA FETCH FREQUENCIES
# Define the data fetch frequencies (1 is a update every loop, 2 is
# every 2nd loop, etc.)
# =====================================================================

FREQUENCY = {
    "MOTOR": 30,
    "IMU": 30,
    "ATTITUDE": 2,
    "ALTITUDE": 100,
    "SONAR": 70,
    "OPTICAL_FLOW": 70,
    "POSITION": 1,
    "VELOCITY": 1,
    "ANALOG": 50,
    "FLAGS": 400,
    "RC": 1,
}

# =====================================================================
# NAVIGATION PLANNER CONFIGURATION
# =====================================================================


class GLOBAL:
    SMOOTH_PATH: bool = True  # Флаг для сглаживания пути в планировщике
    ALGORITHM = (
        PlanningAlgorithm.CARROT  # Алгоритм планирования пути
    )


class OBSTACLE_MAP:
    GRID_RESOLUTION: float = 0.1  # Разрешение сетки для карты препятствий
    SAFETY_MARGIN: float = 0.4  # Запас безопасности для карты препятствий


class MPPI:
    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL

    # Основные параметры MPPI
    TIME_HORIZON: float = 0.15  # Горизонт прогнозирования
    CONTROL_FREQUENCY: float = (
        100.0  # Частота управления (Гц) - для квадрокоптера
    )
    NUM_SAMPLES: int = 2000  # Количество сэмплированных траекторий
    TEMPERATURE: float = 0.2  # Температура для softmax весов

    # Параметры динамической модели
    MAX_LINEAR_VEL: float = 2.0  # Максимальная линейная скорость (м/с)
    MAX_ANGULAR_VEL: float = 1.0  # Максимальная угловая скорость (рад/с)
    MAX_LINEAR_ACCEL: float = 1.0  # Максимальное линейное ускорение (м/с²)
    MAX_ANGULAR_ACCEL: float = 1.0  # Максимальное угловое ускорение (рад/с²)

    # Параметры шума
    VELOCITY_NOISE_STD: float = 0.2  # Стандартное отклонение шума скорости
    ANGULAR_NOISE_STD: float = (
        0.15  # Стандартное отклонение шума угловой скорости
    )
    GUIDANCE_WEIGHT: float = (
        0.5  # Сила смещения сэмплов к цели (0.0 - выкл, 1.0 - макс)
    )

    VELOCITY_TAU: float = 0.2  # Время затухания скорости (с)
    ANGULAR_TAU: float = 0.1  # Время затухания угловой скорости (с)

    # Веса функции стоимости
    PATH_TRACKING_WEIGHT: float = 50.0  # Вес отслеживания пути
    OBSTACLE_AVOIDANCE_WEIGHT: float = 25.0  # Вес избегания препятствий
    CONTROL_PENALTY_WEIGHT: float = 20.0  # Вес штрафа за управление
    GOAL_WEIGHT: float = 40.0  # Вес достижения цели

    # Параметры безопасности
    COLLISION_RADIUS: float = 0.3  # Радиус коллизии дрона (м)
    SAFETY_MARGIN: float = 0.2  # Дополнительный запас безопасности (м)


class DWA:
    pass


class DWB:
    pass


class GRACEFUL:
    pass


class CARROT_PLANNER:
    GRID_RESOLUTION: float = 0.1  # Разрешение сетки для планировщика пути
    SAFETY_MARGIN: float = 0.4  # Запас безопасности для планировщика пути
    VERTICAL_CLEARANCE: float = 0.3  # Вертикальный запас безопасности
    HORIZONTAL_CLEARANCE: float = 0.3  # Горизонтальный запас безопасности
    MAX_SEGMENT_LENGTH: float = 0.2  # Максимальная длина сегмента
    MAX_ITTERATIONS: int = (
        100  # Максимальное количество итераций для планировщика пути
    )


class A_PLANNER:
    pass


class RRT_STAR_PLANNER:
    pass


class SMOOTHER:
    WINDOW_SIZE: int = 3  # Размер окна для усреднения
    MAX_ITTERATIONS: int = 10  # Максимальное количество итераций сглаживания
    ANGULAR_SMOOTHING_FACTOR: float = (
        0.3  # Коэффициент сглаживания углов (0-1)
    )
    MAX_ANGULAR_CHANGE: float = (
        np.pi / 4
    )  # Максимальное изменение угла за сегмент
    SAFETY_MARGIN: float = 0.4  # Минимальное расстояние от препятствий
    MIN_SEGMENT_LENGHT: float = 0.3  # Минимальная длина сегмента
    MAX_SEGMENT_LENGHT: float = 1.0  # Максимальная длина сегмента
    ADAPTIVE_SMOOTHING: bool = True  # Использовать адаптивное сглаживание
    CORNER_DETECTION_THRESHHOLD: float = (
        np.pi / 6
    )  # Порог обнаружения поворотов


class GOAL_CHECKER:
    XY_GOAL_TOLERANCE: float = 0.1  # Допуск по XY координатам в метрах
    Z_GOAL_TOLERANCE: float = 0.05  # Допуск по Z координате в метрах
    YAW_GOAL_TOLERANCE: float = (
        0.1  # Допуск по YAW углу в радианах (~5.7 градусов)
    )
    CHECK_Z: bool = True  # Проверять ли Z координату
    CHECK_YAW: bool = True  # Проверять ли YAW ориентацию


# =====================================================================
# DEVELOPMENT AND TESTING CONFIGURATION
# =====================================================================

# Visual path testing (VPT) configuration
VPT_LINE_COLOR: str = "blue"  # Цвет линии пути
VPT_LINE_WIDTH: float = 3.0  # Ширина линии пути
VPT_WAYPOINT_COLOR: str = "green"  # Цвет маркеров точек пути
VPT_WAYPOINT_SIZE: float = 8.0  # Размер маркеров точек пути
VPT_SHOW_WAYPOINTS: bool = True  # Показывать ли маркеры точек пути
VPT_SHOW_GRID: bool = True  # Показывать ли сетку
VPT_GRID_SPACING: float = 1.0  # Шаг сетки

VPT_LAYOUT_XANCHOR: str = "left"  # Положение графика по оси X
VPT_LAYOUT_X: float = 0.01  # Якорь графика по оси X
VPT_LAYOUT_YANCHOR: str = "top"  # Положение графика по оси Y
VPT_LAYOUT_Y = 0.99  # Якорь графика по оси Y
VPT_LAYOUT_BG_COLOR: str = "rgba(255, 255, 255, 0.7)"  # Цвет фона графика
VPT_LAYOUT_BORDER_COLOR: str = "black"  # Цвет границы графика

VPT_OBSTACLE_BOXES = [
    [[5, 5, 0], [10, 10, 15]],
    [[12, 12, 5], [14, 14, 20]],
    [[16, 16, 0], [18, 18, 10]],
]

# =====================================================================
# NAVIGATION COMMANDS CONFIGURATION
# =====================================================================


class MOVE_COMMAND:
    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL

    # Параметры выполнения команды
    MAX_EXECUTION_TIME: float = 120.0  # Максимальное время выполнения (сек)
    MAX_COORDINATE_VALUE: float = 1000.0  # Максимальные координаты
    MIN_ALTITUDE: float = 0.5  # Минимальная высота (м)
    MAX_ALTITUDE: float = 50.0  # Максимальная высота (м)
    MIN_SAFE_ALTITUDE: float = 1.0  # Минимальная безопасная высота (м)
    MAX_SAFE_TILT_DEG: float = 30.0  # Максимальный безопасный наклон (град)
    MAX_DISTANCE: float = 100.0  # Максимальное расстояние до цели (м)
    MIN_DISTANCE: float = 0.1  # Минимальное расстояние до цели (м)


class TAKEOFF_COMMAND:
    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = True

    DEFAULT_ALTITUDE: float = 2.0  # Высота взлёта по умолчанию (м)
    MIN_ALTITUDE: float = 0.0  # Минимальная высота взлёта (м)
    MAX_ALTITUDE: float = 3.0  # Максимальная высота взлёта (м)

    STABILITY_TIME: float = 2.0  # Время стабилизации после взлёта (сек)

    TIME_DELAY: float = 0.2  # Задержка между командами (сек)
    EXPONENT: float = 5.0  # Экспоненциальный коэффициент для взлёта


class LAND_COMMAND:
    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL

    STABILIZATION_TIME: float = 1.0  # Время стабилизации перед посадкой (сек)

    TIME_DELAY: float = 0.2  # Задержка между командами (сек)
    EXPONENT: float = 5.0  # Экспоненциальный коэффициент для взлёта

    # Дефолтные значения если данные из кеша недоступны
    DEFAULT_ALTITUDE: float = 1.5  # Дефолтная высота для расчета посадки (м)
    DEFAULT_THROTTLE: int = 1500  # Дефолтное значение throttle


class ALTITUDE_COMMAND:
    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL

    MIN_ALTITUDE: float = 0.5  # Минимальная высота (м)
    MAX_ALTITUDE: float = 3.0  # Максимальная высота (м)


class SPEED_COMMAND:
    LOG_LEVEL: str = LOGGER_CONFIG.LOG_LEVEL
    LOG_TO_FILE: bool = LOGGER_CONFIG.LOG_TO_FILE
    LOG_TO_TERMINAL: bool = LOGGER_CONFIG.LOG_TO_TERMINAL

    MAX_LINEAR_SPEED: float = 3.0  # Максимальная линейная скорость (м/с)


# =====================================================================
# DETECTION CONFIGURATION
# =====================================================================


class DETECTION_CONFIG:
    ARUCO_DICT_TYPE: str = "DICT_ORIGINAL"
    ARUCO_MARKER_SIZE: float = 0.05
    BLOB_MIN_AREA: float = 500.0
    BLOB_MAX_BLOBS: int = 10
    BLOB_LOWER_COLOR: Tuple[int, int, int] = (0, 0, 0)
    BLOB_UPPER_COLOR: Tuple[int, int, int] = (255, 255, 255)
    DETECTION_TIMEOUT: float = 1.0

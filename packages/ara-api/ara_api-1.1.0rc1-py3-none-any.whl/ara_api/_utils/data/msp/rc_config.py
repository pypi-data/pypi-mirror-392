"""RC Mapper Configuration"""


class RCConfig:
    MAX_ROLL_VEL: float = 3.0
    MAX_PITCH_VEL: float = 3.0
    MAX_YAW_VEL: float = 2.0

    MAX_THROTTLE: float = 3.0

    MAX_CHANNEL_INPUT: int = 2000
    MIDDLE_CHANNEL_INPUT: int = 1500
    MIN_CHANNEL_INPUT: int = 1000

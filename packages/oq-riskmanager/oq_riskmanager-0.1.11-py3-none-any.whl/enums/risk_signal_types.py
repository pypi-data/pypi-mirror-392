from enum import Enum

class RiskScope(Enum):
    TICK = "tick"
    ORDER = "order"
    GLOBAL = "global"
    SYMBOL = "symbol"


class RiskAction(Enum):
    NONE = "none"
    STOP_OPEN = "stop_open"
    STOP_CLOSE = "stop_close"
    STOP_ALL = "stop_all"
    CLOSE_POSITION = "close_position"


__all__ = ["RiskScope", "RiskAction"]



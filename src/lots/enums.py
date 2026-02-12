from enum import Enum


class LotStatus(str, Enum):
    running = "running"
    ended = "ended"

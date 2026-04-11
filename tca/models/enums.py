from enum import Enum


class Direction(Enum):
    LEFT = -1
    RIGHT = 1

    def opposite(self) -> "Direction":
        return Direction.LEFT if self == Direction.RIGHT else Direction.RIGHT


class Color(Enum):
    RED = (1, 0, 0)
    BLUE = (0, 0, 1)
    GREEN = (0, 1, 0)
    BLACK = (0, 0, 0)
    GRAY = (0.5, 0.5, 0.5)
    WHITE = (1, 1, 1)

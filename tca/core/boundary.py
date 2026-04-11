from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np

from tca.core.grid import Grid


class BoundaryCondition(ABC):
    @abstractmethod
    def wrap_position(self, x: int, length: int) -> int: ...

    @abstractmethod
    def should_remove(self, x: int, length: int, direction_value: int) -> bool: ...

    @abstractmethod
    def find_nearest(self, grid: Grid, lane: int, x: int,
                     direction: int) -> Optional[Tuple[int, int]]: ...


class OpenBoundary(BoundaryCondition):
    def wrap_position(self, x: int, length: int) -> int:
        return x

    def should_remove(self, x: int, length: int, direction_value: int) -> bool:
        if direction_value == 1 and x >= length:
            return True
        if direction_value == -1 and x < 0:
            return True
        return False

    def find_nearest(self, grid: Grid, lane: int, x: int,
                     direction: int) -> Optional[Tuple[int, int]]:
        return grid.find_nearest_in_direction(lane, x, direction)


class CircularBoundary(BoundaryCondition):
    def wrap_position(self, x: int, length: int) -> int:
        return x % length

    def should_remove(self, x: int, length: int, direction_value: int) -> bool:
        return False

    def find_nearest(self, grid: Grid, lane: int, x: int,
                     direction: int) -> Optional[Tuple[int, int]]:
        if lane < 0 or lane >= grid.lane_num:
            return None
        length = grid.length
        if direction == 1:
            rolled = np.roll(grid.cells[lane], -(x + 1))
            nz = np.nonzero(rolled)[0]
            if len(nz) == 0:
                return None
            pos = (x + 1 + int(nz[0])) % length
            return (int(grid.cells[lane, pos]), pos)
        else:
            rolled = np.roll(grid.cells[lane], -x)
            flipped = rolled[::-1]
            nz = np.nonzero(flipped)[0]
            if len(nz) == 0:
                return None
            pos = (x - 1 - int(nz[0])) % length
            return (int(grid.cells[lane, pos]), pos)

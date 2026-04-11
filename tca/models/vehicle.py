from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional

from tca.models.enums import Direction

if TYPE_CHECKING:
    from tca.core.boundary import BoundaryCondition
    from tca.core.grid import Grid


class Vehicle:
    length: int = 1
    width: int = 1
    color: str = "blue"

    def __init__(self, id: int, lane: int, x: int,
                 direction: Direction = Direction.RIGHT):
        self.id = id
        self.lane = lane
        self.x = x
        self.v = 0
        self.direction = direction

    def update_v(self, ctx: VehicleContext) -> None:
        pass

    def need_change_lane(self, ctx: VehicleContext) -> bool:
        return False

    def can_change_lane(self, ctx: VehicleContext,
                        direction: Direction) -> bool:
        return False


class VehicleContext:
    def __init__(self, vehicle: Vehicle, grid: Grid,
                 boundary: BoundaryCondition):
        self._vehicle = vehicle
        self._grid = grid
        self._boundary = boundary

    def _find_in_lane(self, lane: int, direction: int
                      ) -> Optional[tuple]:
        if lane < 0 or lane >= self._grid.lane_num:
            return None
        result = self._boundary.find_nearest(self._grid, lane, self._vehicle.x, direction)
        if result is not None:
            cell_val, pos = result
            if cell_val == self._vehicle.id:
                return None
        return result

    def _gap_for(self, lane: int, direction: int) -> float:
        result = self._find_in_lane(lane, direction)
        if result is None:
            return float('inf')
        cell_val, pos = result
        from tca.core.grid import Grid as G
        from tca.core.boundary import CircularBoundary
        if isinstance(self._boundary, CircularBoundary):
            if direction == 1:
                dist = (pos - self._vehicle.x) % self._grid.length
            else:
                dist = (self._vehicle.x - pos) % self._grid.length
        else:
            dist = abs(pos - self._vehicle.x)
        if cell_val == G.WALL:
            return max(dist - 1, 0)
        target = self._grid.vehicle_objects.get(cell_val)
        target_len = target.length if target else 1
        return max(dist - target_len, 0)

    def _vehicle_for(self, lane: int, direction: int) -> Optional[Vehicle]:
        result = self._find_in_lane(lane, direction)
        if result is None:
            return None
        cell_val, _ = result
        from tca.core.grid import Grid as G
        if cell_val == G.WALL:
            return None
        return self._grid.vehicle_objects.get(cell_val)

    def _right_lane(self) -> int:
        return self._vehicle.lane - self._vehicle.direction.value

    def _left_lane(self) -> int:
        return self._vehicle.lane + self._vehicle.direction.value

    @cached_property
    def gap_front(self) -> float:
        return self._gap_for(self._vehicle.lane, self._vehicle.direction.value)

    @cached_property
    def gap_back(self) -> float:
        return self._gap_for(self._vehicle.lane, -self._vehicle.direction.value)

    @cached_property
    def gap_right_front(self) -> float:
        return self._gap_for(self._right_lane(), self._vehicle.direction.value)

    @cached_property
    def gap_right_back(self) -> float:
        return self._gap_for(self._right_lane(), -self._vehicle.direction.value)

    @cached_property
    def gap_left_front(self) -> float:
        return self._gap_for(self._left_lane(), self._vehicle.direction.value)

    @cached_property
    def gap_left_back(self) -> float:
        return self._gap_for(self._left_lane(), -self._vehicle.direction.value)

    @cached_property
    def front(self) -> Optional[Vehicle]:
        return self._vehicle_for(self._vehicle.lane, self._vehicle.direction.value)

    @cached_property
    def back(self) -> Optional[Vehicle]:
        return self._vehicle_for(self._vehicle.lane, -self._vehicle.direction.value)

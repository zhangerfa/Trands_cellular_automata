from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from tca.models.enums import Direction
from tca.models.vehicle import Vehicle

if TYPE_CHECKING:
    pass


class VehicleGenerator(ABC):
    def __init__(self):
        self._next_id = 1

    def _alloc_id(self) -> int:
        vid = self._next_id
        self._next_id += 1
        return vid

    @abstractmethod
    def initialize(self, road) -> List[Vehicle]:
        return []

    @abstractmethod
    def generate(self, road, time: int) -> List[Vehicle]:
        return []


class PoissonGenerator(VehicleGenerator):
    def __init__(self, vehicle_ratios: dict, lam: float,
                 is_two_way: bool = False):
        super().__init__()
        self.lam = lam
        self.is_two_way = is_two_way
        self._build_cdf(vehicle_ratios)

    def _build_cdf(self, ratios: dict):
        self._cdf = []
        cumulative = 0.0
        for vtype, pct in ratios.items():
            cumulative += pct
            self._cdf.append((cumulative, vtype))

    def _has_arrival(self) -> bool:
        p = 1 - math.exp(-self.lam)
        return random.random() < p

    def _pick_type(self) -> type:
        r = random.random()
        for threshold, vtype in self._cdf:
            if r < threshold:
                return vtype
        return self._cdf[-1][1]

    def initialize(self, road) -> List[Vehicle]:
        return []

    def generate(self, road, time: int) -> List[Vehicle]:
        new_vehicles = []
        directions = [Direction.RIGHT]
        if self.is_two_way:
            directions.append(Direction.LEFT)
        for lane_idx in range(road.lane_num):
            for d in directions:
                if not self._has_arrival():
                    continue
                if not self._has_room(road.grid, lane_idx, d):
                    continue
                vtype = self._pick_type()
                x = 0 if d == Direction.RIGHT else road.length - 1
                v = vtype(id=self._alloc_id(), lane=lane_idx, x=x, direction=d)
                new_vehicles.append(v)
        return new_vehicles

    def _has_room(self, grid, lane: int, direction: Direction) -> bool:
        length = grid.length
        if direction == Direction.RIGHT:
            check_range = range(0, min(3, length))
        else:
            check_range = range(max(length - 3, 0), length)
        for x in check_range:
            if grid.cells[lane, x] != 0:
                return False
        return True


class UniformGenerator(VehicleGenerator):
    def __init__(self, vehicle_ratios: dict, vehicle_num: int):
        super().__init__()
        self.vehicle_num = vehicle_num
        self._type_counts: dict = {}
        for vtype, pct in vehicle_ratios.items():
            self._type_counts[vtype] = round(pct * vehicle_num)

    def initialize(self, road) -> List[Vehicle]:
        lane_num = road.lane_num
        length = road.length
        max_len = max(vtype.length for vtype in self._type_counts)
        gap = max(
            (lane_num * length - self.vehicle_num * max_len) // max(self.vehicle_num, 1),
            1,
        )

        vehicles = []
        lane = 0
        x = 0
        for vtype, count in self._type_counts.items():
            for _ in range(count):
                if lane >= lane_num:
                    break
                v = vtype(id=self._alloc_id(), lane=lane, x=x)
                vehicles.append(v)
                x += max_len + gap
                while x >= length and lane < lane_num:
                    x -= length
                    lane += 1
            if lane >= lane_num:
                break
        return vehicles

    def generate(self, road, time: int) -> List[Vehicle]:
        return []

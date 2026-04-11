from __future__ import annotations

from typing import Any, List, Optional, Tuple

import numpy as np


class Grid:
    EMPTY = 0
    WALL = -1

    def __init__(self, lane_num: int, length: int):
        self.cells = np.zeros((lane_num, length), dtype=np.int32)
        self.vehicle_objects: dict[int, object] = {}
        self.lane_num = lane_num
        self.length = length

    def _occupied_cells(
        self, lane: int, x: int, length: int, width: int, direction_value: int
    ) -> List[Tuple[int, int]]:
        if direction_value == 1:
            xs = [x - i for i in range(length)]
        else:
            xs = [x + i for i in range(length)]
        lanes = [lane - j for j in range(width)]
        out: List[Tuple[int, int]] = []
        for row in lanes:
            for col in xs:
                if 0 <= row < self.lane_num and 0 <= col < self.length:
                    out.append((row, col))
        return out

    def place(
        self,
        vehicle_id: int,
        lane: int,
        x: int,
        length: int,
        width: int,
        direction_value: int,
    ) -> None:
        for row, col in self._occupied_cells(lane, x, length, width, direction_value):
            self.cells[row, col] = vehicle_id

    def remove(
        self,
        vehicle_id: int,
        lane: int,
        x: int,
        length: int,
        width: int,
        direction_value: int,
    ) -> None:
        for row, col in self._occupied_cells(lane, x, length, width, direction_value):
            if self.cells[row, col] == vehicle_id:
                self.cells[row, col] = self.EMPTY

    def place_vehicle(self, vehicle: Any) -> None:
        self.place(
            vehicle_id=vehicle.id,
            lane=vehicle.lane,
            x=vehicle.x,
            length=vehicle.length,
            width=vehicle.width,
            direction_value=vehicle.direction.value,
        )
        self.vehicle_objects[vehicle.id] = vehicle

    def remove_vehicle(self, vehicle: Any) -> None:
        self.remove(
            vehicle_id=vehicle.id,
            lane=vehicle.lane,
            x=vehicle.x,
            length=vehicle.length,
            width=vehicle.width,
            direction_value=vehicle.direction.value,
        )
        self.vehicle_objects.pop(vehicle.id, None)

    def place_wall(self, lane: int, x: int) -> None:
        self.cells[lane, x] = self.WALL

    def place_walls(self, lane: int, start_x: int, end_x: int) -> None:
        self.cells[lane, start_x:end_x] = self.WALL

    def find_nearest_in_direction(
        self, lane: int, x: int, direction: int
    ) -> Optional[Tuple[int, int]]:
        if lane < 0 or lane >= self.lane_num:
            return None
        if direction == 1:
            segment = self.cells[lane, x + 1 :]
            nz = np.nonzero(segment)[0]
            if nz.size == 0:
                return None
            idx = int(nz[0])
            pos = x + 1 + idx
            return int(segment[idx]), pos
        if direction == -1:
            segment = self.cells[lane, :x]
            nz = np.nonzero(segment)[0]
            if nz.size == 0:
                return None
            idx = int(nz[-1])
            return int(segment[idx]), idx
        return None

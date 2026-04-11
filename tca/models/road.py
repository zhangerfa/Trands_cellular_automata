from __future__ import annotations

from typing import TYPE_CHECKING, List

from tca.core.grid import Grid
from tca.models.enums import Direction
from tca.models.vehicle import Vehicle, VehicleContext

if TYPE_CHECKING:
    from tca.core.boundary import BoundaryCondition
    from tca.generator.generator import VehicleGenerator
    from tca.models.lane import Lane


class Road:
    def __init__(self, lanes: List[Lane], generator: VehicleGenerator,
                 boundary: BoundaryCondition):
        self.lanes = lanes
        self.lane_num = len(lanes)
        self.length = max(lane.length for lane in lanes)
        self.grid = Grid(self.lane_num, self.length)
        self.generator = generator
        self.boundary = boundary
        self.vehicles: List[Vehicle] = []
        self._pending_removals: set = set()
        self._init_walls()
        self._init_vehicles()

    def _init_walls(self):
        for i, lane in enumerate(self.lanes):
            if lane.length < self.length:
                self.grid.place_walls(lane=i, start_x=lane.length, end_x=self.length)

    def _init_vehicles(self):
        initial = self.generator.initialize(self)
        for v in initial:
            self.add_vehicle(v)

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        self.grid.place_vehicle(vehicle)

    def remove_vehicle(self, vehicle: Vehicle):
        self.grid.remove_vehicle(vehicle)
        self._pending_removals.add(vehicle.id)

    def _sweep_removed(self):
        if self._pending_removals:
            self.vehicles = [v for v in self.vehicles
                             if v.id not in self._pending_removals]
            self._pending_removals.clear()

    def generate_vehicles(self, time: int):
        new_vehicles = self.generator.generate(self, time)
        for v in new_vehicles:
            self.add_vehicle(v)

    def update_velocities(self):
        for v in self.vehicles:
            if v.id in self._pending_removals:
                continue
            ctx = VehicleContext(v, self.grid, self.boundary)
            v.update_v(ctx)

    def do_lane_changes(self):
        for v in self.vehicles:
            if v.id in self._pending_removals:
                continue
            ctx = VehicleContext(v, self.grid, self.boundary)
            if v.need_change_lane(ctx):
                for d in Direction:
                    if v.can_change_lane(ctx, d):
                        self._execute_lane_change(v, d)
                        break

    def _execute_lane_change(self, vehicle: Vehicle, direction: Direction):
        self.grid.remove_vehicle(vehicle)
        vehicle.lane -= vehicle.direction.value * direction.value
        self.grid.place_vehicle(vehicle)

    def move_vehicles(self):
        for v in self.vehicles:
            if v.id in self._pending_removals:
                continue
            self.grid.remove_vehicle(v)
            new_x = v.x + v.v * v.direction.value
            if self.boundary.should_remove(new_x, self.length, v.direction.value):
                self._pending_removals.add(v.id)
                self.grid.vehicle_objects.pop(v.id, None)
                continue
            v.x = self.boundary.wrap_position(new_x, self.length)
            self.grid.place_vehicle(v)
        self._sweep_removed()

from tca.models.road import Road
from tca.models.lane import Lane
from tca.models.vehicle import Vehicle
from tca.models.enums import Direction
from tca.core.boundary import OpenBoundary, CircularBoundary
from tca.core.grid import Grid
from tca.generator.generator import PoissonGenerator, UniformGenerator


class SimpleCar(Vehicle):
    length = 1
    v_max = 5

    def update_v(self, ctx):
        gap = ctx.gap_front
        effective_gap = min(gap, self.v_max + 1)
        self.v = min(self.v + 1, self.v_max, int(effective_gap))

    def need_change_lane(self, ctx):
        return ctx.gap_front < self.v_max

    def can_change_lane(self, ctx, direction):
        if direction == Direction.RIGHT:
            return ctx.gap_right_front > ctx.gap_front and ctx.gap_right_back > self.v_max
        else:
            return ctx.gap_left_front > ctx.gap_front and ctx.gap_left_back > self.v_max


class TestRoadInit:
    def test_basic_creation(self):
        lanes = [Lane({"普通": 50})]
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.3)
        road = Road(lanes, gen, OpenBoundary())
        assert road.lane_num == 1
        assert road.length == 50
        assert len(road.vehicles) == 0

    def test_walls_placed_for_short_lane(self):
        lanes = [Lane({"普通": 50}), Lane({"普通": 30})]
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.3)
        road = Road(lanes, gen, OpenBoundary())
        assert road.length == 50
        assert road.grid.cells[1, 30] == Grid.WALL
        assert road.grid.cells[1, 49] == Grid.WALL
        assert road.grid.cells[1, 29] == Grid.EMPTY

    def test_circular_init_vehicles(self):
        lanes = [Lane({"普通": 100})]
        gen = UniformGenerator({SimpleCar: 1.0}, vehicle_num=5)
        road = Road(lanes, gen, CircularBoundary())
        assert len(road.vehicles) == 5


class TestRoadOperations:
    def test_update_velocities(self):
        lanes = [Lane({"普通": 100})]
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.0)
        road = Road(lanes, gen, OpenBoundary())
        v = SimpleCar(id=1, lane=0, x=10)
        road.add_vehicle(v)
        road.update_velocities()
        assert v.v == 1

    def test_move_vehicles_open(self):
        lanes = [Lane({"普通": 20})]
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.0)
        road = Road(lanes, gen, OpenBoundary())
        v = SimpleCar(id=1, lane=0, x=10)
        v.v = 3
        road.add_vehicle(v)
        road.move_vehicles()
        assert v.x == 13

    def test_move_vehicles_circular_wrap(self):
        lanes = [Lane({"普通": 100})]
        gen = UniformGenerator({SimpleCar: 1.0}, vehicle_num=0)
        road = Road(lanes, gen, CircularBoundary())
        v = SimpleCar(id=1, lane=0, x=98)
        v.v = 5
        road.add_vehicle(v)
        road.move_vehicles()
        assert v.x == 3

    def test_move_vehicles_open_exit(self):
        lanes = [Lane({"普通": 20})]
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.0)
        road = Road(lanes, gen, OpenBoundary())
        v = SimpleCar(id=1, lane=0, x=18)
        v.v = 5
        road.add_vehicle(v)
        road.move_vehicles()
        assert v not in road.vehicles

    def test_do_lane_changes(self):
        lanes = [Lane({"普通": 100}), Lane({"普通": 100})]
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.0)
        road = Road(lanes, gen, OpenBoundary())
        blocker = SimpleCar(id=2, lane=0, x=12)
        road.add_vehicle(blocker)
        v = SimpleCar(id=1, lane=0, x=10)
        road.add_vehicle(v)
        road.do_lane_changes()
        assert v.lane == 1

from tca.models.vehicle import Vehicle, VehicleContext
from tca.models.enums import Direction
from tca.core.grid import Grid
from tca.core.boundary import OpenBoundary, CircularBoundary


class TestVehicle:
    def test_default_vehicle(self):
        v = Vehicle(id=1, lane=0, x=5)
        assert v.id == 1
        assert v.lane == 0
        assert v.x == 5
        assert v.v == 0
        assert v.direction == Direction.RIGHT
        assert v.length == 1
        assert v.width == 1

    def test_custom_direction(self):
        v = Vehicle(id=1, lane=0, x=5, direction=Direction.LEFT)
        assert v.direction == Direction.LEFT

    def test_subclass_overrides(self):
        class BigCar(Vehicle):
            length = 3
            color = "red"
        v = BigCar(id=1, lane=0, x=5)
        assert v.length == 3


def _place(grid, v):
    grid.place_vehicle(v)


class TestVehicleContext:
    def test_gap_front_with_vehicle_ahead(self):
        grid = Grid(lane_num=1, length=20)
        v1 = Vehicle(id=1, lane=0, x=5)
        v2 = Vehicle(id=2, lane=0, x=10)
        _place(grid, v1)
        _place(grid, v2)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_front == 4  # 10 - 5 - 1 (target length)

    def test_gap_front_no_vehicle(self):
        grid = Grid(lane_num=1, length=20)
        v1 = Vehicle(id=1, lane=0, x=5)
        _place(grid, v1)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_front == float('inf')

    def test_gap_front_wall(self):
        grid = Grid(lane_num=1, length=20)
        v1 = Vehicle(id=1, lane=0, x=5)
        _place(grid, v1)
        grid.place_wall(lane=0, x=8)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_front == 2  # 8 - 5 - 1

    def test_gap_back(self):
        grid = Grid(lane_num=1, length=20)
        v1 = Vehicle(id=1, lane=0, x=10)
        v2 = Vehicle(id=2, lane=0, x=5)
        _place(grid, v1)
        _place(grid, v2)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_back == 4

    def test_gap_right_front(self):
        grid = Grid(lane_num=2, length=20)
        v1 = Vehicle(id=1, lane=1, x=5)
        v2 = Vehicle(id=2, lane=0, x=10)
        _place(grid, v1)
        _place(grid, v2)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_right_front == 4

    def test_gap_left_front(self):
        grid = Grid(lane_num=3, length=20)
        v1 = Vehicle(id=1, lane=1, x=5)
        v2 = Vehicle(id=2, lane=2, x=12)
        _place(grid, v1)
        _place(grid, v2)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_left_front == 6

    def test_gap_right_no_lane(self):
        grid = Grid(lane_num=2, length=20)
        v1 = Vehicle(id=1, lane=0, x=5)
        _place(grid, v1)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_right_front == float('inf')

    def test_front_vehicle_object(self):
        grid = Grid(lane_num=1, length=20)
        v1 = Vehicle(id=1, lane=0, x=5)
        v2 = Vehicle(id=2, lane=0, x=10)
        _place(grid, v1)
        _place(grid, v2)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.front is v2

    def test_circular_gap_wraps(self):
        grid = Grid(lane_num=1, length=100)
        v1 = Vehicle(id=1, lane=0, x=95)
        v2 = Vehicle(id=2, lane=0, x=3)
        _place(grid, v1)
        _place(grid, v2)
        ctx = VehicleContext(v1, grid, CircularBoundary())
        assert ctx.gap_front == 7  # 95->...->3, distance 8, minus length 1 = 7

    def test_cached_property(self):
        grid = Grid(lane_num=1, length=20)
        v1 = Vehicle(id=1, lane=0, x=5)
        _place(grid, v1)
        ctx = VehicleContext(v1, grid, OpenBoundary())
        assert ctx.gap_front is ctx.gap_front

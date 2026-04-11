from tca.core.boundary import OpenBoundary, CircularBoundary
from tca.core.grid import Grid


class TestOpenBoundary:
    def test_wrap_position_no_change(self):
        b = OpenBoundary()
        assert b.wrap_position(5, 100) == 5

    def test_should_remove_right_exit(self):
        b = OpenBoundary()
        assert b.should_remove(x=100, length=100, direction_value=1) is True

    def test_should_remove_left_exit(self):
        b = OpenBoundary()
        assert b.should_remove(x=-1, length=100, direction_value=-1) is True

    def test_should_not_remove_inside(self):
        b = OpenBoundary()
        assert b.should_remove(x=50, length=100, direction_value=1) is False

    def test_find_nearest_basic(self):
        b = OpenBoundary()
        grid = Grid(lane_num=1, length=20)
        grid.cells[0, 10] = 2
        result = b.find_nearest(grid, lane=0, x=5, direction=1)
        assert result == (2, 10)

    def test_find_nearest_no_wrap(self):
        b = OpenBoundary()
        grid = Grid(lane_num=1, length=20)
        grid.cells[0, 3] = 2
        result = b.find_nearest(grid, lane=0, x=5, direction=1)
        assert result is None


class TestCircularBoundary:
    def test_wrap_position_no_wrap(self):
        b = CircularBoundary()
        assert b.wrap_position(5, 100) == 5

    def test_wrap_position_overflow(self):
        b = CircularBoundary()
        assert b.wrap_position(103, 100) == 3

    def test_wrap_position_underflow(self):
        b = CircularBoundary()
        assert b.wrap_position(-2, 100) == 98

    def test_should_remove_never(self):
        b = CircularBoundary()
        assert b.should_remove(x=100, length=100, direction_value=1) is False
        assert b.should_remove(x=-1, length=100, direction_value=-1) is False

    def test_find_nearest_wraps_forward(self):
        b = CircularBoundary()
        grid = Grid(lane_num=1, length=100)
        grid.cells[0, 3] = 2
        result = b.find_nearest(grid, lane=0, x=95, direction=1)
        assert result is not None
        vid, pos = result
        assert vid == 2
        assert pos == 3

    def test_find_nearest_wraps_backward(self):
        b = CircularBoundary()
        grid = Grid(lane_num=1, length=100)
        grid.cells[0, 97] = 2
        result = b.find_nearest(grid, lane=0, x=3, direction=-1)
        assert result is not None
        vid, pos = result
        assert vid == 2
        assert pos == 97

    def test_find_nearest_no_other_vehicle(self):
        b = CircularBoundary()
        grid = Grid(lane_num=1, length=100)
        result = b.find_nearest(grid, lane=0, x=50, direction=1)
        assert result is None

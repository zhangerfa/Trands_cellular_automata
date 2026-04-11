import numpy as np

from tca.core.grid import Grid


class TestGridPlaceRemove:
    def test_empty_grid(self):
        grid = Grid(lane_num=2, length=10)
        assert grid.cells.shape == (2, 10)
        assert np.all(grid.cells == Grid.EMPTY)

    def test_place_vehicle_single_cell(self):
        grid = Grid(lane_num=1, length=10)
        grid.place(vehicle_id=1, lane=0, x=5, length=1, width=1, direction_value=1)
        assert grid.cells[0, 5] == 1

    def test_place_vehicle_multi_cell(self):
        grid = Grid(lane_num=1, length=10)
        grid.place(vehicle_id=1, lane=0, x=5, length=3, width=1, direction_value=1)
        assert grid.cells[0, 5] == 1
        assert grid.cells[0, 4] == 1
        assert grid.cells[0, 3] == 1
        assert grid.cells[0, 2] == Grid.EMPTY

    def test_remove_vehicle(self):
        grid = Grid(lane_num=1, length=10)
        grid.place(vehicle_id=1, lane=0, x=5, length=2, width=1, direction_value=1)
        grid.remove(vehicle_id=1, lane=0, x=5, length=2, width=1, direction_value=1)
        assert np.all(grid.cells == Grid.EMPTY)

    def test_place_wall(self):
        grid = Grid(lane_num=1, length=10)
        grid.place_wall(lane=0, x=8)
        assert grid.cells[0, 8] == Grid.WALL

    def test_place_walls_range(self):
        grid = Grid(lane_num=1, length=10)
        grid.place_walls(lane=0, start_x=7, end_x=10)
        assert grid.cells[0, 7] == Grid.WALL
        assert grid.cells[0, 8] == Grid.WALL
        assert grid.cells[0, 9] == Grid.WALL
        assert grid.cells[0, 6] == Grid.EMPTY

    def test_place_multi_width(self):
        grid = Grid(lane_num=3, length=10)
        grid.place(vehicle_id=1, lane=1, x=5, length=1, width=2, direction_value=1)
        assert grid.cells[1, 5] == 1
        assert grid.cells[0, 5] == 1


class TestGridFindNearest:
    def test_find_right_basic(self):
        grid = Grid(lane_num=1, length=20)
        grid.cells[0, 10] = 2
        result = grid.find_nearest_in_direction(lane=0, x=5, direction=1)
        assert result == (2, 10)

    def test_find_right_no_vehicle(self):
        grid = Grid(lane_num=1, length=20)
        result = grid.find_nearest_in_direction(lane=0, x=5, direction=1)
        assert result is None

    def test_find_left_basic(self):
        grid = Grid(lane_num=1, length=20)
        grid.cells[0, 3] = 2
        result = grid.find_nearest_in_direction(lane=0, x=8, direction=-1)
        assert result == (2, 3)

    def test_find_skips_empty(self):
        grid = Grid(lane_num=1, length=20)
        grid.cells[0, 10] = 2
        grid.cells[0, 15] = 3
        result = grid.find_nearest_in_direction(lane=0, x=5, direction=1)
        assert result == (2, 10)

    def test_find_detects_wall(self):
        grid = Grid(lane_num=1, length=20)
        grid.cells[0, 10] = Grid.WALL
        result = grid.find_nearest_in_direction(lane=0, x=5, direction=1)
        assert result == (Grid.WALL, 10)

    def test_find_invalid_lane(self):
        grid = Grid(lane_num=2, length=20)
        result = grid.find_nearest_in_direction(lane=-1, x=5, direction=1)
        assert result is None
        result = grid.find_nearest_in_direction(lane=2, x=5, direction=1)
        assert result is None

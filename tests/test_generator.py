import math
import random
from unittest.mock import MagicMock

import numpy as np

from tca.generator.generator import PoissonGenerator, UniformGenerator
from tca.models.vehicle import Vehicle
from tca.models.enums import Direction


class SimpleCar(Vehicle):
    length = 2
    color = "red"


class SimpleTruck(Vehicle):
    length = 4
    color = "blue"


def _make_mock_road(lane_num=2, length=100):
    road = MagicMock()
    road.lane_num = lane_num
    road.length = length
    road.grid = MagicMock()
    road.grid.lane_num = lane_num
    road.grid.length = length
    road.grid.cells = np.zeros((lane_num, length), dtype="int32")
    return road


class TestPoissonGenerator:
    def test_arrival_probability_correct(self):
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.3)
        random.seed(42)
        arrivals = sum(gen._has_arrival() for _ in range(100_000))
        rate = arrivals / 100_000
        expected = 1 - math.exp(-0.3)
        assert abs(rate - expected) < 0.02

    def test_generate_returns_vehicles(self):
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=5.0)
        road = _make_mock_road(lane_num=1, length=20)
        random.seed(42)
        vehicles = gen.generate(road, time=0)
        assert all(isinstance(v, SimpleCar) for v in vehicles)

    def test_initialize_returns_empty(self):
        gen = PoissonGenerator({SimpleCar: 1.0}, lam=0.3)
        road = _make_mock_road()
        assert gen.initialize(road) == []


class TestUniformGenerator:
    def test_initialize_correct_count(self):
        gen = UniformGenerator({SimpleCar: 1.0}, vehicle_num=10)
        road = _make_mock_road(lane_num=2, length=100)
        vehicles = gen.initialize(road)
        assert len(vehicles) == 10

    def test_initialize_respects_ratios(self):
        gen = UniformGenerator({SimpleCar: 0.6, SimpleTruck: 0.4}, vehicle_num=10)
        road = _make_mock_road(lane_num=2, length=200)
        vehicles = gen.initialize(road)
        cars = sum(1 for v in vehicles if isinstance(v, SimpleCar))
        trucks = sum(1 for v in vehicles if isinstance(v, SimpleTruck))
        assert cars == 6
        assert trucks == 4

    def test_generate_returns_empty(self):
        gen = UniformGenerator({SimpleCar: 1.0}, vehicle_num=10)
        road = _make_mock_road()
        assert gen.generate(road, time=0) == []

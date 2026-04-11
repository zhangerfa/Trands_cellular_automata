from tca.core.simulation import Simulation
from tca.core.boundary import OpenBoundary, CircularBoundary
from tca.models.road import Road
from tca.models.lane import Lane
from tca.models.vehicle import Vehicle
from tca.detector.detector import Detector
from tca.generator.generator import PoissonGenerator, UniformGenerator


class NaSchCar(Vehicle):
    length = 1
    v_max = 5

    def update_v(self, ctx):
        gap = ctx.gap_front
        effective_gap = min(gap, self.v_max + 1)
        self.v = min(self.v + 1, self.v_max, int(effective_gap))


class TestSimulation:
    def test_step_advances_time(self):
        lanes = [Lane({"普通": 100})]
        gen = PoissonGenerator({NaSchCar: 1.0}, lam=0.0)
        road = Road(lanes, gen, OpenBoundary())
        sim = Simulation(road)
        assert sim.time == 0
        sim.step()
        assert sim.time == 1

    def test_run_multiple_steps(self):
        lanes = [Lane({"普通": 100})]
        gen = PoissonGenerator({NaSchCar: 1.0}, lam=0.0)
        road = Road(lanes, gen, OpenBoundary())
        sim = Simulation(road)
        sim.run(steps=50)
        assert sim.time == 50

    def test_vehicles_move_each_step(self):
        lanes = [Lane({"普通": 100})]
        gen = UniformGenerator({NaSchCar: 1.0}, vehicle_num=0)
        road = Road(lanes, gen, CircularBoundary())
        v = NaSchCar(id=1, lane=0, x=10)
        road.add_vehicle(v)
        sim = Simulation(road)
        sim.step()
        assert v.v == 1
        assert v.x == 11

    def test_no_collision_after_many_steps(self):
        lanes = [Lane({"普通": 200}), Lane({"普通": 200})]
        gen = UniformGenerator({NaSchCar: 1.0}, vehicle_num=20)
        road = Road(lanes, gen, CircularBoundary())
        sim = Simulation(road)
        for _ in range(200):
            sim.step()
            for lane_idx in range(road.lane_num):
                row = road.grid.cells[lane_idx]
                vehicle_ids = row[row > 0]
                assert len(vehicle_ids) == len(set(vehicle_ids)), \
                    f"Collision at step {sim.time}"

    def test_detector_integration(self):
        lanes = [Lane({"普通": 100})]
        gen = UniformGenerator({NaSchCar: 1.0}, vehicle_num=0)
        road = Road(lanes, gen, CircularBoundary())
        v = NaSchCar(id=1, lane=0, x=10)
        road.add_vehicle(v)
        det = Detector(start_time=0, end_time=100, start_x=0, end_x=100)
        sim = Simulation(road, detector=det)
        sim.run(steps=5)
        assert 1 in det._active

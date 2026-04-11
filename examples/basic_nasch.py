"""Basic NaSch model example: single lane, circular boundary."""
import random

from tca import (
    Vehicle, Lane, Road, Simulation, Detector,
    CircularBoundary, UniformGenerator, Plotter,
)


class NaSchCar(Vehicle):
    length = 1
    v_max = 5
    color = "blue"
    _p_slow = 0.3

    def update_v(self, ctx):
        gap = ctx.gap_front
        effective_gap = min(gap, self.v_max + 1)
        self.v = min(self.v + 1, self.v_max, int(effective_gap))
        if random.random() < self._p_slow and self.v > 0:
            self.v -= 1


def main():
    lanes = [Lane({"road": 200})]
    generator = UniformGenerator({NaSchCar: 1.0}, vehicle_num=40)
    detector = Detector(start_time=100)
    road = Road(lanes, generator, CircularBoundary())

    sim = Simulation(road, detector)
    sim.run(steps=5000)
    print("Results:", detector.summary())


if __name__ == "__main__":
    main()

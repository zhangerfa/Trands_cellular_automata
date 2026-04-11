"""Multi-lane work zone example with lane closure."""
import random

from tca import (
    Vehicle, Lane, Road, Simulation, Detector,
    OpenBoundary, PoissonGenerator, Direction,
)


class Car(Vehicle):
    length = 2
    v_max = 7
    color = "blue"

    def update_v(self, ctx):
        gap = ctx.gap_front
        effective_gap = min(gap, self.v_max + 1)
        self.v = min(self.v + 1, self.v_max, int(effective_gap))
        if random.random() < 0.2 and self.v > 0:
            self.v = max(self.v - 1, 0)

    def need_change_lane(self, ctx):
        return ctx.gap_front < self.v_max

    def can_change_lane(self, ctx, direction):
        if direction == Direction.RIGHT:
            return (ctx.gap_right_front > ctx.gap_front
                    and ctx.gap_right_back > self.v_max)
        else:
            return (ctx.gap_left_front > ctx.gap_front
                    and ctx.gap_left_back > self.v_max)


class Truck(Car):
    length = 4
    v_max = 5
    color = "red"


def main():
    lanes = [
        Lane({"普通车道": 100, "变窄路段": 50, "施工路段": 50}),
        Lane({"普通车道": 100, "变窄路段": 50, "施工路段": 50}),
        Lane({"普通车道": 100, "变窄路段": 50}),
    ]
    generator = PoissonGenerator({Car: 0.8, Truck: 0.2}, lam=0.4)
    detector = Detector(start_time=200, start_x=50, end_x=180)
    road = Road(lanes, generator, OpenBoundary())

    sim = Simulation(road, detector)
    sim.run(steps=10000)
    print("Results:", detector.summary())


if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tca.detector.detector import Detector
    from tca.models.road import Road


class Simulation:
    def __init__(self, road: Road, detector: Detector = None):
        self.road = road
        self.detector = detector
        self.time = 0

    def step(self):
        self.road.generate_vehicles(self.time)
        self.road.do_lane_changes()
        self.road.update_velocities()
        self.road.move_vehicles()
        if self.detector:
            self.detector.detect(self.time, self.road.vehicles)
        self.time += 1

    def run(self, steps: int):
        for _ in range(steps):
            self.step()

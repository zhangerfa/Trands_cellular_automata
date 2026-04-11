from __future__ import annotations

import math
import random

from tca.models.vehicle import Vehicle, VehicleContext
from tca.models.enums import Direction


class Auto(Vehicle):
    """Autonomous driving vehicle with deterministic car-following."""
    length = 5
    v_max = 30
    color = "red"
    _accel = 3

    def update_v(self, ctx: VehicleContext) -> None:
        gap = ctx.gap_front
        gap_safe = 1
        v_safe = 1
        if gap > gap_safe:
            self.v = min(v_safe, self.v + self._accel, self.v_max, int(gap))
        elif gap < gap_safe:
            self.v = max(min(v_safe, int(gap)), 0)
        else:
            self.v = min(self.v, int(gap))

    def need_change_lane(self, ctx: VehicleContext) -> bool:
        return ctx.gap_front < self.v_max

    def can_change_lane(self, ctx: VehicleContext,
                        direction: Direction) -> bool:
        if direction == Direction.RIGHT:
            target_front = ctx.gap_right_front
            target_back = ctx.gap_right_back
        else:
            target_front = ctx.gap_left_front
            target_back = ctx.gap_left_back
        return target_front > ctx.gap_front and target_back > self.v_max


class Car(Auto):
    """Human-driven vehicle with stochastic slowdown."""
    color = "blue"

    def update_v(self, ctx: VehicleContext) -> None:
        super().update_v(ctx)
        p_slow = self._get_p_slow()
        if random.random() < p_slow:
            self.v = max(self.v - 4, 0)

    def _get_p_slow(self, density: float = 100.0) -> float:
        m = 200
        return 0.1 + 0.4 * ((1 + m * math.exp(-0.05 * density)) ** (1 / -0.95))


BUILTIN_VEHICLES = {
    "Auto": Auto,
    "Car": Car,
}

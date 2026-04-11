from __future__ import annotations

from typing import List

import pandas as pd

from tca.models.vehicle import Vehicle


class Detector:
    def __init__(self, start_time: int = 0, end_time: float = float('inf'),
                 start_x: int = 0, end_x: float = float('inf')):
        self.start_time = start_time
        self.end_time = end_time
        self.start_x = start_x
        self.end_x = end_x
        self._active: dict = {}
        self._completed: list = []
        self.flow = 0

    def detect(self, time: int, vehicles: List[Vehicle]):
        for v in vehicles:
            if self._should_detect(time, v):
                if v.id not in self._active:
                    self._on_enter(v)
                self._record(v)
            elif v.id in self._active:
                self._on_exit(v)

    def _should_detect(self, time: int, vehicle: Vehicle) -> bool:
        return (self.start_time <= time <= self.end_time
                and self.start_x <= vehicle.x <= self.end_x)

    def _on_enter(self, vehicle: Vehicle):
        self._active[vehicle.id] = {
            "vehicle_id": vehicle.id,
            "v_sum": 0,
            "detect_times": 0,
        }

    def _record(self, vehicle: Vehicle):
        record = self._active[vehicle.id]
        record["v_sum"] += vehicle.v
        record["detect_times"] += 1

    def _on_exit(self, vehicle: Vehicle):
        self.flow += 1
        record = self._active.pop(vehicle.id)
        self._completed.append(record)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self._completed)

    def finalize(self):
        """Move all still-active vehicles to completed (call at end of simulation)."""
        for vid in list(self._active.keys()):
            record = self._active.pop(vid)
            self._completed.append(record)

    def summary(self) -> dict:
        all_records = self._completed + list(self._active.values())
        if not all_records:
            return {"average_speed": 0.0, "flow": self.flow}
        df = pd.DataFrame(all_records)
        valid = df[df["detect_times"] > 0]
        if valid.empty:
            return {"average_speed": 0.0, "flow": self.flow}
        avg_speeds = valid["v_sum"] / valid["detect_times"]
        return {
            "average_speed": float(avg_speeds.mean()),
            "flow": self.flow,
        }

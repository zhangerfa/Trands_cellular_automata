from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import patches

if TYPE_CHECKING:
    from tca.core.simulation import Simulation
    from tca.models.road import Road


class Plotter:
    def __init__(self, road: Road, figsize: tuple = (14, 3)):
        self.road = road
        self.figsize = figsize

    def draw_frame(self, ax: plt.Axes, time: int) -> None:
        ax.clear()
        grid = self.road.grid
        lane_num = grid.lane_num
        length = grid.length

        ax.set_facecolor("#f0f0f0")
        ax.set_xlim(-0.5, length - 0.5)
        ax.set_ylim(-0.5, lane_num - 0.5)
        ax.set_aspect("equal")
        ax.invert_yaxis()

        for y in range(1, lane_num):
            ax.axhline(y - 0.5, color="white", linewidth=1.5, linestyle="--")
        ax.axhline(-0.5, color="#333", linewidth=2)
        ax.axhline(lane_num - 0.5, color="#333", linewidth=2)

        for lane_idx in range(lane_num):
            wall_mask = grid.cells[lane_idx] == grid.WALL
            wall_xs = np.nonzero(wall_mask)[0]
            for wx in wall_xs:
                rect = patches.Rectangle(
                    (wx - 0.5, lane_idx - 0.5), 1, 1,
                    facecolor="#888", edgecolor="none")
                ax.add_patch(rect)

        color_map = {}
        for v in self.road.vehicles:
            vtype = type(v).__name__
            if vtype not in color_map:
                color_map[vtype] = v.color if isinstance(v.color, str) else "blue"
            for dx in range(v.length):
                cx = v.x - dx * v.direction.value
                if 0 <= cx < length:
                    rect = patches.Rectangle(
                        (cx - 0.5, v.lane - 0.5), 1, 1,
                        facecolor=color_map[vtype],
                        edgecolor="white", linewidth=0.5)
                    ax.add_patch(rect)

        for lane_idx, lane in enumerate(self.road.lanes):
            pos = 0
            for sec_type, sec_len in lane.sections.items():
                pos += sec_len
                if pos < length:
                    ax.axvline(pos - 0.5,
                               ymin=(lane_num - lane_idx - 1) / lane_num,
                               ymax=(lane_num - lane_idx) / lane_num,
                               color="orange", linewidth=1, linestyle=":")

        ax.set_title(f"t = {time}    vehicles = {len(self.road.vehicles)}",
                     fontsize=10, loc="left")
        ax.set_xlabel("Position (cell)")
        ax.set_ylabel("Lane")
        ax.set_yticks(range(lane_num))
        ax.set_yticklabels([f"L{i}" for i in range(lane_num)])

        if color_map:
            legend_handles = [
                patches.Patch(facecolor=c, label=name)
                for name, c in color_map.items()
            ]
            ax.legend(handles=legend_handles, loc="upper right", fontsize=8)

    def animate(self, simulation: Simulation, steps: int,
                interval: float = 50) -> FuncAnimation:
        fig, ax = plt.subplots(figsize=self.figsize)

        def update(frame):
            simulation.step()
            self.draw_frame(ax, simulation.time)

        anim = FuncAnimation(fig, update, frames=steps,
                             interval=interval, repeat=False)
        return anim

    def save(self, path: str, simulation: Simulation,
             steps: int, fps: int = 20) -> None:
        anim = self.animate(simulation, steps, interval=1000 // fps)
        writer = "pillow" if path.endswith(".gif") else "ffmpeg"
        anim.save(path, writer=writer, fps=fps)
        plt.close()

    def plot_spacetime(self, simulation: Simulation, steps: int,
                       lane: int = 0) -> plt.Figure:
        length = self.road.length
        diagram = np.zeros((steps, length), dtype=np.int8)

        for t in range(steps):
            simulation.step()
            for v in self.road.vehicles:
                if v.lane == lane:
                    for dx in range(v.length):
                        cx = v.x - dx * v.direction.value
                        if 0 <= cx < length:
                            diagram[t, cx] = 1

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(diagram, cmap="binary", aspect="auto",
                  origin="lower", interpolation="none")
        ax.set_xlabel("Position (cell)")
        ax.set_ylabel("Time step")
        ax.set_title(f"Space-Time Diagram (Lane {lane})")
        return fig

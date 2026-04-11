from __future__ import annotations

from typing import Optional

import click
import yaml

from tca.core.boundary import OpenBoundary, CircularBoundary
from tca.core.simulation import Simulation
from tca.detector.detector import Detector
from tca.generator.generator import PoissonGenerator, UniformGenerator
from tca.models.lane import Lane
from tca.models.road import Road
from tca.rules.builtin import BUILTIN_VEHICLES


def _load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _build_from_config(config: dict):
    road_cfg = config["road"]
    lanes = [Lane(l["sections"]) for l in road_cfg["lanes"]]

    boundary_name = road_cfg.get("boundary", "open")
    boundary = CircularBoundary() if boundary_name == "circular" else OpenBoundary()

    gen_cfg = config["generator"]
    ratios = {}
    for name, pct in gen_cfg["vehicles"].items():
        if name not in BUILTIN_VEHICLES:
            raise click.ClickException(f"Unknown vehicle type: {name}")
        ratios[BUILTIN_VEHICLES[name]] = pct

    gen_type = gen_cfg["type"]
    if gen_type == "poisson":
        generator = PoissonGenerator(
            ratios, lam=gen_cfg["lam"],
            is_two_way=gen_cfg.get("is_two_way", False))
    elif gen_type == "uniform":
        generator = UniformGenerator(ratios, vehicle_num=gen_cfg["vehicle_num"])
    else:
        raise click.ClickException(f"Unknown generator type: {gen_type}")

    det_cfg = config.get("detector", {})
    detector = Detector(
        start_time=det_cfg.get("start_time", 0),
        end_time=det_cfg.get("end_time", float("inf")),
        start_x=det_cfg.get("start_x", 0),
        end_x=det_cfg.get("end_x", float("inf")),
    )

    road = Road(lanes, generator, boundary)
    return road, detector


@click.group()
def main():
    """TCA - Traffic Cellular Automata simulation framework."""
    pass


@main.command()
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--steps", default=1000, help="Number of simulation steps")
@click.option("--output", default=None, help="Output CSV path")
def run(config_path: str, steps: int, output: Optional[str]):
    """Run simulation and output results."""
    config = _load_config(config_path)
    road, detector = _build_from_config(config)
    sim = Simulation(road, detector)
    sim.run(steps)

    summary = detector.summary()
    for k, v in summary.items():
        click.echo(f"{k}: {v}")

    if output:
        df = detector.to_dataframe()
        df.to_csv(output, index=False)
        click.echo(f"Data saved to {output}")


@main.command()
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--steps", default=500, help="Number of simulation steps")
@click.option("--interval", default=50.0, help="Animation interval in ms")
@click.option("--save", "save_path", default=None, help="Save animation to file")
def show(config_path: str, steps: int, interval: float,
         save_path: Optional[str]):
    """Show simulation animation."""
    import matplotlib.pyplot as plt
    from tca.viz.plot import Plotter

    config = _load_config(config_path)
    road, detector = _build_from_config(config)
    sim = Simulation(road, detector)
    plotter = Plotter(road)

    if save_path:
        plotter.save(save_path, sim, steps)
        click.echo(f"Animation saved to {save_path}")
    else:
        anim = plotter.animate(sim, steps, interval=interval)
        plt.show()

"""TCA - Traffic Cellular Automata simulation framework."""

from tca.models.vehicle import Vehicle, VehicleContext
from tca.models.lane import Lane
from tca.models.road import Road
from tca.models.enums import Direction, Color
from tca.core.simulation import Simulation
from tca.core.boundary import OpenBoundary, CircularBoundary
from tca.detector.detector import Detector
from tca.generator.generator import (
    VehicleGenerator, PoissonGenerator, UniformGenerator,
)
from tca.viz.plot import Plotter

__all__ = [
    "Vehicle", "VehicleContext", "Lane", "Road",
    "Direction", "Color",
    "Simulation", "OpenBoundary", "CircularBoundary",
    "Detector",
    "VehicleGenerator", "PoissonGenerator", "UniformGenerator",
    "Plotter",
]

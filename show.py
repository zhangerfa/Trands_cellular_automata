from road import *
from lane import *
from draw import *

### 仿真场景展示
L3 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50},
          {VehicleType.car: 0.9, VehicleType.truck: 0.1})
L2 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50},
          {VehicleType.car: 1, VehicleType.truck: 0})
L1 = Lane({LaneType.M0: 100, LaneType.M1: 50},
          {VehicleType.car: 1, VehicleType.truck: 0})
lanes = [L1, L2, L3]
time = 100
road = Road(lanes)
show(road, time)
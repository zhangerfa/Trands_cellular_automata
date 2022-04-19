# 车辆信息枚举类
from enum import Enum


# 车辆颜色枚举类
class Color(Enum):
    red = [1, 0, 0]
    blue = [0, 0, 1]
    green = [0, 1, 0]
    black = [0, 0, 0]


# 车辆前进方向枚举类
class Direction(Enum):
    left = -1
    right = 1
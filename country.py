from vehicle import Vehicle
from vehicle_enum import *
# 单独行人类
class Pedstrain(Vehicle):
    def __init__(self, id, lane, x, direction):
        super().__init__(id, lane, x, direction)
        self.v_max = 2
        self.width = 1
        self.length = 1
        self.color = Color.green
        self.d = self.v  # 行人若减速即停止
        self.a = self.v_max  # 行人速度只有 0 和 v_max


class TwoPedstrain(Vehicle):
    def __init__(self, id, lane, x, direction):
        super().__init__(id, lane, x, direction)
        self.v_max = 2
        self.width = 2
        self.length = 1
        self.color = Color.blue
        self.d = self.v_max  # 行人若减速即停止
        self.a = self.v_max  # 行人速度只有 0 和 v_max
        self.static_time = 0  # 结对行人静止时间，超过2s就会变为前后排队
        self.is_queue = False  # 标记当前是否为排队状态

class Bike(Vehicle):
    def __init__(self, id, lane, x, direction, is_impulsive):
        super().__init__(id, lane, x, direction)
        self.is_impulsive = is_impulsive  # 是否为冲动驾驶员控制
        self.length = 2
        # 最大车速取决于驾驶员类型
        self.v_max = 6 if self.is_impulsive else 4
        self.color = Color.red
        self.d = 1  # 减速度
        self.a = 1  # 加速度


class Motor(Vehicle):
    def __init__(self, id, lane, x, direction, is_impulsive):
        super().__init__(id, lane, x, direction)
        self.is_impulsive = is_impulsive  # 是否为冲动驾驶员控制
        self.length = 2
        self.v_max = 8 if self.is_impulsive else 6
        self.color = Color.black
        self.d = 2
        self.a = 2

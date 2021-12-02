'''
车辆数据结构
所有长度单位为元胞（3.75 * 3.75）
'''

from enum import Enum


# 车辆状态枚举类
class Status(Enum):
    static = 3
    slow = 2
    fast = 1


# 车辆颜色枚举类
class Color(Enum):
    red = [1, 0, 0]
    blue = [0, 0, 1]
    green = [0, 1, 0]


class Vehicle():

    def __init__(self, id , lane, x):
        self.id = id # int 用于唯一标识车辆
        self.x = x  # 车道方向位置 车头所在元胞位置
        self.v = 0 # 车辆车速
        self.lane = lane  # 车辆位于车道
        self.status = Status.static  # 车辆状态
        self.front = None  # 前车
        self.back = None  # 后车
        self.left_front = None  # 左前车
        self.right_front = None  # 右前车
        self.left_back = None  # 左后车
        self.right_back = None  # 右后车


# 小汽车类
class Car(Vehicle):
    length = 2  # 车辆长度
    color = Color.red  # 车辆颜色
    sp = 2  # dt时间内车辆平均行驶的距离
    s_max = 4  # 在dt时间内车辆的最大行驶距离 也就是v_max
    gap_desire = 12  # 期望前车距


# 货车类
class Truck(Vehicle):
    length = 4
    color = Color.blue
    sp = 2
    s_max = 3
    gap_desire = 9

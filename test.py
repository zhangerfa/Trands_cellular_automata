# 用于方法测试

from road import *
from vehicle_generator import Vehicle_generator
from vehicle import Vehicle
from enum import Enum
from vehicle_enum import Color, Direction

# 测试车辆周围车辆信息
def test_around(road):
    # 添加测试车辆
    x = 0
    for i in range(1, 6):
        if i % 2 == 0:
            v = Car(i, 0, x, road)
            x += 4
        else:
            v = Truck(i, 0, x, road, Direction.left)
            x += 5
        road.add_vehicle(v)

    x = 1
    for i in range(6, 10):
        if i % 2 == 0:
            v = Car(i, 1, x, road)
            x += 6
        else:
            v = Truck(i, 1, x, road)
            x += 4
        road.add_vehicle(v)

    x = 19
    for i in range(10, 16):
        if i % 2 == 0:
            v = Car(i, 2, x, road)
            x -= 6
        else:
            v = Truck(i, 2, x, road)
            x -= 4
        road.add_vehicle(v)

    road.toString()
    for v in road.vehicles:
        v.toString()

# 小汽车类
class Car(Vehicle):

    def __init__(self, index, lane, x, road, direction=Direction.right):
        super().__init__(index, lane, x, road, direction)
        self.length = 2  # 车辆长度
        self.color = Color.red  # 车辆颜色
        self.sp = 2  # dt时间内车辆平均行驶的距离
        self.s_max = 4  # 在dt时间内车辆的最大行驶距离 也就是v_max
        self.gap_desire = 12  # 期望前车距

    # 更新车速
    def __update_v(self):
        self.v = 10

    # 判断能否向传入方向换道
    def can_change_lane(self, direction):
        pass

    # 将车辆换道至传入车道
    def update_lane(self, desire_lane):
        pass


# 货车类
class Truck(Vehicle):

    def __init__(self, index, lane, x, road, direction=Direction.right):
        super().__init__(index, lane, x, road, direction)
        self.length = 4
        self.color = Color.blue
        self.sp = 2
        self.s_max = 3
        self.gap_desire = 9

    # 更新车速
    def __update_v(self):
        self.v = 10


# 创建车道类型
class LaneType(Enum):
    M0 = '测试道路'


# 创建车辆生成器
lam = 0.4  # 到达率
vehicle_generator = Vehicle_generator({Car: 0.9, Truck: 0.1}, lam)

# 创建车道对象
L1 = Lane({LaneType.M0: 20})
L2 = Lane({LaneType.M0: 20})
L3 = Lane({LaneType.M0: 20})
lanes = [L1, L2, L3]
# 创建道路
road = Road(lanes, vehicle_generator, True)

test_around(road)
a = road.space.space[0][9]
print(f'\n{a.back.index}')

# road.show(time_max)
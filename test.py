# 测试内容
from road import *
from vehicle_generator import Vehicle_generator
from vehicle import Vehicle, Color
from enum import Enum
from draw import show, draw

#### 创建仿真使用的车辆类
'''
需要实现 
void update_v()
如果换道规则中 优先向右侧（相对于车辆前进方向）换道 需要实现
boolean can_change_lane(direction, road) 判断能否向传入方向换道 direction 为Direction 对象
void update_lane(lane) 将车辆换道至传入车道
否则  需要重写road.change_lane(road) 仍然建议实现上述两个方法，
并基于这两个方法实现road.change_lane(road),以提高可读性
'''


# 小汽车类
class Car(Vehicle):
    length = 2  # 车辆长度
    color = Color.red  # 车辆颜色
    sp = 2  # dt时间内车辆平均行驶的距离
    s_max = 4  # 在dt时间内车辆的最大行驶距离 也就是v_max
    gap_desire = 12  # 期望前车距

    # 更新车速
    def __update_v(self):
        self.v = 10

    # 判断能否向传入方向换道
    def can_change_lane(self, direction, road):
        pass

    # 将车辆换道至传入车道
    def update_lane(self, desire_lane, road):
        pass


# 货车类
class Truck(Vehicle):
    length = 4
    color = Color.blue
    sp = 2
    s_max = 3
    gap_desire = 9

    # 更新车速
    def __update_v(self):
        self.v = 10

#### 构建测试场景
# 创建车道类型
class LaneType(Enum):
    M0 = '战场路段'
    M1 = '缩减路段'
    M2 = '施工路段'

# 创建车辆生成器
lam = 0.4 # 到达率
vehicle_generator = Vehicle_generator({Car: 0.9, Truck: 0.1}, lam)

# 创建车道对象
L1 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50})
L2 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50})
L3 = Lane({LaneType.M0: 100, LaneType.M1: 50})
lanes = [L1, L2, L3]
# 创建道路
road = Road(lanes, vehicle_generator)

#### 运行仿真
time_max = 100

# road.run(time_max)

show(road, time_max)

#### 检测器数据整理
# 仿真
import random
from road import *
from vehicle_generator import Vehicle_generator
from vehicle import Vehicle
from enum import Enum
from draw import draw
from vehicle_enum import Color


#### 创建仿真使用的车辆类

# 小汽车类
class Car(Vehicle):
    a_max = 4  # 最大加速度
    color = Color.red  # 车辆颜色
    v_max = 7  # 最大速度
    gap_desire = 12  # 期望前车距
    p = 0.2  # 随机慢化概率
    p2 = 0.35  # M1段车道3处随机慢化概率

    def __init__(self, index, lane, x, road, direction):
        super().__init__(index, lane, x, road, direction)
        self.length = 2  # 车辆长度

    # 更新车速
    def _update_v(self):
        gap = self.get_gap()
        a = random.randint(1, self.a_max)
        self.v = min(self.v + a, self.v_max, gap)
        # 车辆在M1段
        section = self.get_section()
        condition1 = section == Section.M1
        # 车辆在施工车道
        lane_length = self.get_lane_length()
        condition2 = lane_length < self.driving_on.length
        if condition1 and condition2:
            p_slow = self.p2
        else:
            p_slow = self.p
        if random.random() < p_slow:
            self.v = max(self.v - a, 0)

    def change_lane(self):
        '''
        优先向非施工车道换道
        :return:
        '''
        if self._need_change_lane():
            # 需要换道判断向哪换道
            if self.lane == 0:
                if self._can_change_lane(Direction.left):
                    self.lane = self.lane + 1
            elif self.lane == 2:
                if self._can_change_lane(Direction.right):
                    self.lane = self.lane - 1
            else:
                # 施工车道
                bulid_lane = 0 if self.driving_on.space.lanes[0].length < self.driving_on.length else 2
                directions = [Direction.left, Direction.right] if bulid_lane == 0 else [Direction.right, Direction.left]
                for direction in directions:
                    if self._can_change_lane(direction):
                        if direction == Direction.right:
                            self.lane = self.lane - 1
                        else:
                            self.lane = self.lane + 1
                        break

    # 判断能否向传入方向换道
    def _can_change_lane(self, direction):
        '''
        目标车道前车距 ＞ 当前车道前车距 且 目标车道后车距 ＞ 最大车速
        :param direction: 换道方向 为 Direction枚举类对向
        :return: 能否向传入方向换道
        '''
        gap = self.get_gap()  # 前车距
        if direction == Direction.right:
            gap_desire_front = self.get_gap_right()  # 右前车距
            gap_desire_back = self.get_gap_back_right()  # 右后车距
        else:
            gap_desire_front = self.get_gap_left()  # 左前车距
            gap_desire_back = self.get_gap_back_left()  # 右后车距
        if gap_desire_front > gap and gap_desire_back > self.v_max:
            return True
        else:
            return False

    # 判断是否需要换道
    def _need_change_lane(self):
        '''
        如果前车距 ＜ 最大车速 则换道
        :return: 是否换道
        '''
        gap = self.get_gap()  # 前车距
        if gap < self.v_max:
            return True
        else:
            return False


# 货车类
class Truck(Car):
    a_max = 2  # 最大加速度
    color = Color.blue  # 车辆颜色
    v_max = 5  # 最大速度
    gap_desire = 12  # 期望前车距
    p = 0.3  # 随机慢化概率

    def __init__(self, index, lane, x, road, direction):
        super().__init__(index, lane, x, road, direction)
        self.length = 4

    # 判断能否向传入方向换道
    def can_change_lane(self, direction):
        pass

    # 将车辆换道至传入车道
    def update_lane(self, desire_lane):
        pass


# 墙体类
class Wall(Vehicle):
    color = Color.black

    # 墙体永远不会移动， 且会阻碍车辆移动
    def _update_v(self):
        v = 0


#### 构建测试场景
# 创建车道类型
class Section(Enum):
    M0 = '战场路段'
    M1 = '缩减路段'
    M2 = '施工路段'


# 创建车辆生成器
lam = 0.4  # 到达率
vehicle_generator = Vehicle_generator({Car: 0.5, Truck: 0.5}, lam)

# 创建车道对象
L1 = Lane({Section.M0: 10})
L2 = Lane({Section.M0: 10})
L3 = Lane({Section.M0: 10})
lanes = [L1, L2, L3]
# 创建道路
road = Road(lanes, vehicle_generator)
# 向施工车道添加墙体
a = Wall(666, 2, 7, road)
road.add_vehicle(a)

#### 运行仿真
time_max = 30
for time in range(time_max):
    road.update()
    road.toString()
    for v in road.vehicles:
        v.toString()

road.show(time_max)
import math
import random

from src.draw import Drawer
from src.road import *
from src.simulation import Simulation
from src.vehicle_generator import Vehicle_generator
from src.vehicle import Vehicle
from src.vehicle_enum import Color, Direction
from src.detector import Detector


# 创建仿真使用的车辆类
# 自动驾驶类
class Auto(Vehicle):
    a = 3  # 加速度
    b = 4  # 减速度
    color = Color.red  # 车辆颜色
    v_max = 30  # 最大速度
    length = 5  # 车辆长度

    # 更新车速
    def update_v(self):
        is_forefront = self.__is_forefront()  # 判断是否为头车
        if is_forefront:
            # 头车0.2概率静止
            if random.random() < 0.2:
                self.v = 0
                return
        gap = max(self.get_front_gap(), 0)
        gap_safe = 1
        v_safe = 1
        if gap > gap_safe:
            self.v = min(v_safe, self.v + self.a, self.v_max, gap)
        elif gap < gap_safe:
            self.v = max(min(v_safe, gap), 0)
        else:
            # 匀速
            self.v = min(self.v, gap)

    # 判断车辆是否为头车
    def __is_forefront(self):
        if self.get_front_gap() + self.length > self.road.length:
            return True
        return False

    # 判断能否向传入方向换道
    def can_change_lane(self, direction):
        """
        目标车道前车距 ＞ 当前车道前车距 且 目标车道后车距 ＞ 最大车速
        :param direction: 换道方向 为 Direction枚举类对向
        :return: 能否向传入方向换道
        """
        gap = self.__get_gap()  # 前车距
        if direction == Direction.right:
            if self.lane == 0:
                return False
            gap_desire_front = self.get_right_front_gap()  # 右前车距
            gap_desire_back = self.get_gap_back_right()  # 右后车距
        else:
            if self.lane == self.road.lane_num - 1:
                return False
            gap_desire_front = self.get_left_front_gap()  # 左前车距
            gap_desire_back = self.get_gap_back_left()  # 左后车距
        if gap_desire_front > gap and gap_desire_back > self.v_max:
            return True
        else:
            return False

    # 判断是否需要换道
    def need_change_lane(self):
        """
        如果前车距 ＜ 最大车速 则换道
        :return: 是否换道
        """
        gap = self.get_front_gap()  # 前车距
        if gap < self.v_max:
            return True
        else:
            return False


# 手动驾驶车类
class Car(Auto):
    color = Color.blue  # 车辆颜色

    def update_v(self):
        super(Car, self).update_v()
        # 随机慢化
        rou = 100
        if random.random() < get_p_slow(rou):
            self.v = max(self.v - self.b, 0)


# 计算随机慢化概率
def get_p_slow(rou):
    M = 200  # 1千米长的道路上所能容纳的最大车辆数
    return 0.1 + 0.4 * ((1 + M * math.exp(-0.05 * rou)) ** (1 / (-0.95)))


if __name__ == '__main__':
    # 创建车辆生成器
    vehicle_num = 60
    vehicle_generator = Vehicle_generator({Car: 0.5, Auto: 0.5},
                                          vehicle_num=vehicle_num)
    # 创建车道对象
    lane_length = 100  # 2000
    lanes = [{'普通车道': lane_length}] * 3
    # 创建检测器
    detector = Detector()
    # 创建道路
    r = Road(lanes)
    run_time = 200  # 仿真时间
    # 创建仿真对象
    simulation = Simulation(r, vehicle_generator, detector)
    # 仿真展示
    drawer = Drawer(simulation)
    drawer.show(100)
    # 获取检测器数据
    data = simulation.run(run_time)

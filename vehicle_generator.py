import random
from math import exp
from vehicle_enum import Direction


# 车辆生成器
class Vehicle_generator:
    # vehicle_type_percent {type ： percent}
    def __init__(self, vehicle_type_percent_dict, lam):
        self.lam = lam  # 泊松分布 λ 参数 dt时间内平均到达车辆数
        self.vehicle_count = 1  # 生成交通参与者计数器
        # 生成各类交通参与者的概率区间 如（0，0.1）生成car （0.1，1）生成truck
        self.range_type = {}
        percent_sum = 0
        for vehicle_type in vehicle_type_percent_dict:
            percent = vehicle_type_percent_dict[vehicle_type]
            percent_sum += percent
            self.range_type[percent_sum] = vehicle_type
            # 当某种车百分百出现 其他车不会生成
            if percent == 1:
                break

    # 返回新生成的交通参与者 如果无法生成返回None
    '''
    @:param : direction 在道路一侧生成该行驶方向的车辆，默认为向右
    '''

    def new_vehicle(self, lane, road, direction=Direction.right):
        new_vehicle = None
        # 当前车道如果有空间 且有车辆到达则生成一个车辆对象
        if self.__has_vehicle() and has_room(lane, road):
            random_num = random.random()
            # 以一定比例生成不同种类车辆
            for max_of_range in self.range_type:
                # max_of_range 为该类车辆区间上限
                vehicle_type = self.range_type[max_of_range]
                if max_of_range > random_num:
                    x = road.length - 1 if direction == Direction.left else 1
                    new_vehicle = vehicle_type(self.vehicle_count, lane, x, road)
                    self.vehicle_count += 1
                    break
        return new_vehicle

    # 交通参与者到达率服从泊松分布
    def __has_vehicle(self):
        poisson = self.lam * exp(self.lam)  # dt足够小，只计算dt时间内来一辆车概率
        random_num = random.random()
        if random_num < poisson:
            return True
        else:
            return False


# 传入车道 有 3 个空元胞时 则认为有供新到达车辆生成的空间
def has_room(lane, road):
    for x in range(3):
        if road.space.index_space[lane][x] != 0:
            return False
    return True

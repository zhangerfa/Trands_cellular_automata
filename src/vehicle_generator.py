import random
from math import exp
from src.vehicle_enum import Direction


# 车辆生成器
class Vehicle_generator:
    """
    @:param is_two_way 标记道路上是否包含两个方向行驶车辆,当is_two_way为True时，两侧分别生成向左向右的车辆
    @:param vehicle_type_percent {type ： percent}
    @:param vehicle_num 周期边界条件时，车辆总数
    当不传入 vehicle_type_percent_dict 和 lam时，则为周期边界条件，一次性生成所有车辆
    """

    def __init__(self, vehicle_type_percent_dict, lam=None, vehicle_num=0,
                 is_two_way=False):
        self.lam = lam  # 泊松分布 λ 参数 dt时间内平均到达车辆数
        self.is_two_way = is_two_way
        self.vehicle_count = 1  # 生成交通参与者计数器
        self.vehicle_num = vehicle_num  # 空间占有率
        self.vehicle_space = 0  # 车辆占据空间总长度（目前只在周期边界条件下统计）
        percent_sum = 0
        if lam is not None:
            # 生成各类交通参与者的概率区间 如（0，0.1）生成car （0.1，1）生成truck
            self.range_type = {}
            for vehicle_type, percent in vehicle_type_percent_dict.items():
                percent_sum += percent
                self.range_type[percent_sum] = vehicle_type
                # 当某种车百分百出现 其他车不会生成
                if percent == 1:
                    break
        else:
            self.type_num_dict = {}
            for vehicle_type, percent in vehicle_type_percent_dict.items():
                self.type_num_dict[vehicle_type] = round(percent * self.vehicle_num)

    def __update_vehicle_space(self, vehicle):
        self.vehicle_space += vehicle.length

    # 等间距生成周期边界条件时道路所有车辆，以车辆对象的list返回
    def init_all_vehicles(self, road):
        if self.lam is not None:
            print('传入λ，则执行开口条件，不能调用此方法')
            return

        lane_num = road.lane_num
        road_length = road.length

        new_vehicles = []  # 存储所有新生成的车辆

        lane = 0
        x = 0
        gap = (lane_num * road_length - self.vehicle_num * self.get_max_vehicle_length()) // self.vehicle_num
        for vehicle_type, num in self.type_num_dict.items():
            for i in range(num):
                new_vehicle = vehicle_type(self.vehicle_count, lane, x, road)
                self.vehicle_count += 1
                new_vehicles.append(new_vehicle)

                lane += 1
                if lane == lane_num:
                    x = x + gap + self.get_max_vehicle_length()
                    lane = 0

        return new_vehicles

    # 获取传入车辆中最大车长度
    def get_max_vehicle_length(self):
        res = 0  # 最大车长
        for vehicle_type in self.type_num_dict:
            tmp = vehicle_type(-1, -1, -1, None)
            res = max(res, tmp.length)
        return res

    # 返回新生成的交通参与者 如果无法生成返回None
    '''
    @:param : direction 在道路一侧生成该行驶方向的车辆，默认为向右
    '''

    def new_vehicle(self, lane, road):
        new_vehicles = []  # 存储所有新生成的车辆
        new_vehicle = None
        # 生成车辆的方向列表
        directions = [Direction.right, Direction.left] if self.is_two_way else [Direction.right]
        for direction in directions:
            # 当前车道如果有空间 且有车辆到达则生成一个车辆对象
            if self.__has_vehicle() and has_room(lane, road.space.space, direction):
                random_num = random.random()
                # 以一定比例生成不同种类车辆
                for max_of_range in self.range_type:
                    # max_of_range 为该类车辆区间上限
                    vehicle_type = self.range_type[max_of_range]
                    if max_of_range > random_num:
                        x = road.length - 1 if direction == Direction.left else 1
                        if self.is_two_way:
                            new_vehicle = vehicle_type(self.vehicle_count, lane, x, road, direction)
                        else:
                            new_vehicle = vehicle_type(self.vehicle_count, lane, x, road)
                        self.vehicle_count += 1
                        break
            new_vehicles.append(new_vehicle)
        return new_vehicles

    # 交通参与者到达率服从泊松分布
    def __has_vehicle(self):
        poisson = self.lam * exp(self.lam)  # dt足够小，只计算dt时间内来一辆车概率
        random_num = random.random()
        if random_num < poisson:
            return True
        else:
            return False


# 传入车道 有 3 个空元胞时 则认为有供新到达车辆生成的空间
def has_room(lane, space, direction):
    """
    :param direction: 生成车辆方向 为 Direction枚举类对象
    :param space:
    :param lane: 车道index
    :return:
    """
    road_length = len(space[0])
    x_range = range(3) if direction == Direction.right else range(road_length - 3, road_length)
    if direction == Direction.left:
        print()
    for x in x_range:
        if space[lane][x] != 0:
            return False
    return True

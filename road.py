'''
道路数据结构
道路由车道构成  并对道路上多有车辆状态进行更新
对外提供 run() 方法 运行仿真
'''
import random
from lane import *
from vehicle import *
import vehicles as vs
from detector import M1_detector


class Road():
    def __init__(self, lanes):
        self.lanes = lanes  # 车道组成，lane list
        self.lane_num = len(lanes)  # 车道数
        self.length = 0  # 道路长度为所有车道的最大长度
        self.vehicle_count = 1  # 道路生成车辆计数器
        self.space = []  # 存储道路离散空间 无车 0 有车 车id
        self.shortest_lane = 0  # 长度最短路段序号
        self.m1_decorator = M1_detector(self, 1500) # 道路检测器
        for lane in lanes:
            self.space.append([0] * lane.length)
            if self.length < lane.length:
                self.length = lane.length
            if lane.length < self.lanes[self.shortest_lane].length:
                self.shortest_lane = self.lanes.index(lane)
        # 向施工路段增加一辆永不移动的车辆以保持求车距函数的一致性
        c = Car(-1, self.shortest_lane, self.lanes[self.shortest_lane].length - 1)
        self.lanes[self.shortest_lane].vehicles.append(c)
        self.update_space()
        self.update_around()

    # 道路开口新车辆到达
    def new_vehicle_arrive(self):
        for l in self.lanes:
            vehicles = l.vehicles
            # 判断是否有位置供新到达车辆生成
            lane_index = self.lanes.index(l)
            for x in range(4):
                if self.space[lane_index][x] != 0:
                    return
            # 有空间 以泊松分布 有车辆到达
            if l.is_arrive():
                random_num = random.random()
                # 以一定比例生成不同种类车辆
                for key in l.type_percent:
                    # key 为该类车辆区间上限
                    if key > random_num:
                        type = l.type_percent[key]
                        lane = self.lanes.index(l)
                        if type == VehicleType.car:
                            v = Car(self.vehicle_count, lane, 1)
                            self.vehicle_count += 1
                        elif type == VehicleType.truck:
                            v = Truck(self.vehicle_count, lane, 1)
                            self.vehicle_count += 1
                        # 新生成车辆放在 车道的车辆list第0个
                        l.vehicles.append(v)
                        # 初始化新车的周围车辆信息
                        self.update_vehicle_around(v)
                        break

    # 更新车辆两侧车辆信息
    def update_vehicle_around(self, vehicle):
        # 更新前后车
        vehicle.front = self.find_front_vehicle(vehicle.lane, vehicle)
        vehicle.back = self.find_back_vehicle(vehicle.lane, vehicle)
        # 更新左侧前后车
        if vehicle.lane == 0:
            vehicle.left_front = None
            vehicle.left_back = None
        else:
            vehicle.left_front = self.find_front_vehicle(vehicle.lane - 1, vehicle)
            vehicle.left_back = self.find_back_vehicle(vehicle.lane - 1, vehicle)
        # 更新右侧前后车
        if vehicle.lane == 2:
            vehicle.right_back = None
            vehicle.right_front = None
        else:
            vehicle.right_front = self.find_front_vehicle(vehicle.lane + 1, vehicle)
            vehicle.right_back = self.find_back_vehicle(vehicle.lane + 1, vehicle)

    # 寻找车辆在某一车道的的前车
    def find_front_vehicle(self, lane, vehicle):
        for x in range(min(vehicle.x + 1, len(self.space[lane])), len(self.space[lane])):
            if self.space[lane][x] != 0:
                front_id = self.space[lane][x]
                for v in self.lanes[lane].vehicles:
                    if v.id == front_id:
                        return v
        return None

    # 寻找车辆的后车
    def find_back_vehicle(self, lane, vehicle):
        if lane == self.shortest_lane:
            start_x = self.lanes[self.shortest_lane].length - 1
        else:
            start_x = max(vehicle.x - vehicle.length, 0)
        if vehicle not in self.lanes[lane].vehicles:
            return None
        for x in range(start_x, -1, -1):
            if self.space[lane][x] != 0:
                back_id = self.space[lane][x]
                for v in self.lanes[lane].vehicles:
                    if v.id == back_id:
                        return v
        return None

    def update_space(self):
        self.space = []  # 存储空间矩阵形状（值全为0）
        for lane in self.lanes:
            self.space.append([0] * lane.length)
        for lane in self.lanes:
            vehicles = lane.vehicles
            for v in vehicles:
                for i in range(v.length):
                    cur_x = min(v.x - i, lane.length - 1)
                    if cur_x >= 0:
                        self.space[v.lane][cur_x] = v.id

    # 更新整个道路上所有车辆状态
    def update_status(self):
        for lane in self.lanes:
            vehicles = lane.vehicles
            for v in vehicles:
                # 如果车辆位于施工车道，且距离施工区不足sp停止
                vs.update_status(v)

    # 更新整个道路上所有车辆周围车辆信息
    '''
    注意 update_around() 是 基于space的，所以一定要先update_space()
    '''

    def update_around(self):
        for lane in self.lanes:
            vehicles = lane.vehicles
            for v in vehicles:
                # 向施工路段增加一辆永不移动的车辆以保持求车距函数的一致性
                if v.id == -1:
                    continue
                self.update_vehicle_around(v)

    # 更新整个道路上所有车辆位置
    def update_x(self):
        # 更新车辆状态
        self.update_space()
        self.update_around()
        self.update_status()
        # 更新车辆位置
        for lane in self.lanes:
            vehicles = lane.vehicles
            for v in vehicles:
                # 向施工路段增加一辆永不移动的车辆以保持求车距函数的一致性
                if v.id == -1:
                    continue
                vs.update_x(v)
                # 如果车辆释出车道将该车辆从该车道的车辆list中删除
                if v.x >= lane.length:
                    lane.vehicles.remove(v)

        # 更新space矩阵
        self.update_space()
        # 位置更新完之后更新所有车辆周围车辆信息
        self.update_around()

    # 判断能否向右侧换道
    def can_right_change_lane(self, vehicle):
        condition1 = vehicle.status == Status.slow
        condition2 = vs.get_gap_right(vehicle) >= vehicle.gap_desire
        condition3 = vehicle.status == Status.static
        condition4 = vs.get_gaph_right(vehicle) >= vehicle.s_max
        condition5 = vs.get_gap_right(vehicle) >= vehicle.sp
        return (condition1 and condition2 and condition4) or \
               (condition3 and condition5 and condition4)

    # 判断能否向左侧换道
    def can_left_change_lane(self, vehicle):
        condition1 = vehicle.status == Status.slow
        condition2 = vs.get_gap_left(vehicle) >= vehicle.gap_desire
        condition3 = vehicle.status == Status.static
        condition4 = vs.get_gaph_left(vehicle) >= vehicle.s_max
        condition5 = vs.get_gap_left(vehicle) >= vehicle.sp
        return (condition1 and condition2 and condition4) or \
               (condition3 and condition5 and condition4)

    # 向右侧换道
    def change_lane_right(self, vehicle):
        cur_lane = vehicle.lane
        vehicle.lane = cur_lane + 1
        self.lanes[cur_lane].vehicles.remove(vehicle)
        self.lanes[vehicle.lane].vehicles.append(vehicle)
        # 向检测器发送换道信息
        if vehicle in self.m1_decorator.detecing_vehicles:
            cur_times = self.m1_decorator.detecing_vehicles[vehicle]['change_lane_times']
            self.m1_decorator.detecing_vehicles[vehicle]['change_lane_times'] = cur_times + 1

    # 向做侧换道
    def change_lane_left(self, vehicle):
        cur_lane = vehicle.lane
        vehicle.lane = cur_lane - 1
        self.lanes[cur_lane].vehicles.remove(vehicle)
        self.lanes[vehicle.lane].vehicles.append(vehicle)
        # 向检测器发送换道信息
        if vehicle in self.m1_decorator.detecing_vehicles:
            cur_times = self.m1_decorator.detecing_vehicles[vehicle]['change_lane_times']
            self.m1_decorator.detecing_vehicles[vehicle]['change_lane_times'] = cur_times + 1

    # 单车换道
    def one_vehicle_change_lane(self, vehicle):
        section = self.lanes[vehicle.lane].which_section(vehicle)
        if self.shortest_lane == 0:
            # 左侧施工，优先向右换道
            if section == LaneType.M0 or section == LaneType.M2:
                # 正常路段或施工路段
                if vehicle.lane == 1:
                    if self.can_right_change_lane(vehicle):
                        self.change_lane_right(vehicle)
                    elif self.can_left_change_lane(vehicle):
                        self.change_lane_left(vehicle)
                elif vehicle.lane == 0:
                    if self.can_right_change_lane(vehicle):
                        self.change_lane_right(vehicle)
                else:
                    if self.can_left_change_lane(vehicle):
                        self.change_lane_left(vehicle)
            else:
                # 缩减路段
                if vehicle.lane == 2:
                    # 非施工路段可自由换道
                    if self.can_left_change_lane(vehicle):
                        self.change_lane_left(vehicle)
                elif vehicle.lane == 1:
                    # 中间路段可自由向非施工路段换道
                    if self.can_right_change_lane(vehicle):
                        self.change_lane_right(vehicle)
                    elif vehicle.status == Status.static:
                        # 中间车道车辆只有在静止情况下可以向施工路段换道
                        condition1 = vs.get_gaph_left(vehicle) > vehicle.s_max
                        condition2 = vs.get_gap_left(vehicle) > vehicle.sp
                        if condition1 and condition2:
                            self.change_lane_left(vehicle)
                else:
                    # 施工路段车辆强致换道中间车道
                    if self.can_right_change_lane(vehicle):
                        self.change_lane_right(vehicle)
        else:
            # 右侧施工、优先向左换道
            if section == LaneType.M0 or section == LaneType.M2:
                # 正常路段或施工路段
                if vehicle.lane == 1:
                    if self.can_left_change_lane(vehicle):
                        self.change_lane_left(vehicle)
                    elif self.can_right_change_lane(vehicle):
                        self.change_lane_right(vehicle)
                elif vehicle.lane == 0:
                    if self.can_right_change_lane(vehicle):
                        self.change_lane_right(vehicle)
                else:
                    if self.can_left_change_lane(vehicle):
                        self.change_lane_left(vehicle)
            else:
                # 缩减路段
                if vehicle.lane == 0:
                    # 非施工路段可自由换道
                    if self.can_right_change_lane(vehicle):
                        self.change_lane_right(vehicle)
                elif vehicle.lane == 1:
                    # 中间路段可自由向非施工路段换道
                    if self.can_left_change_lane(vehicle):
                        self.change_lane_left(vehicle)
                    elif vehicle.status == Status.static:
                        # 中间车道车辆只有在静止情况下可以向施工路段换道
                        condition1 = vs.get_gaph_right(vehicle) > vehicle.s_max
                        condition2 = vs.get_gap_right(vehicle) > vehicle.sp
                        if condition1 and condition2:
                            self.change_lane_right(vehicle)
                else:
                    # 施工路段车辆强致换道中间车道
                    if self.can_left_change_lane(vehicle):
                        self.change_lane_left(vehicle)

    # 道路上所有车辆完成换道
    def change_lane(self):
        # 更新车辆位置
        for lane in self.lanes:
            vehicles = lane.vehicles
            for v in vehicles:
                # 向施工路段增加一辆永不移动的车辆以保持求车距函数的一致性
                if v.id == -1:
                    continue
                self.one_vehicle_change_lane(v)
        # 更新道路状态
        self.update_space()
        self.update_around()

    # 运行仿真
    def run(self, time_max):
        for time in range(time_max):
            # 开口新车辆到达
            self.new_vehicle_arrive()
            # 车辆换道
            self.change_lane()
            # 车辆位置更新
            self.update_x()
            # M1段检测器检测
            self.m1_decorator.detect(time)
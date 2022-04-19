from src.vehicle import Wall
from src.vehicle_enum import Direction
from src.draw import draw
from src.space import Space
import matplotlib.pyplot as plt

'''
@:param vehicle_generator 车辆生成器，用于生成车辆
（开口生成器就运行开口边界条件，等间距生成器就运行周期边界条件）
'''


class Road:
    def __init__(self, lanes, vehicle_generator, detector=None):
        self.vehicles = []  # 道路上所有车辆对象列表
        self.vehicle_generator = vehicle_generator  # 车辆生成器
        self.detector = detector  # 检测器
        self.length = max([x.length for x in lanes])  # 最大车道长度为道路长度
        # 判断是周期边界条件还是开口边界条件
        self.is_circle_border = True if self.vehicle_generator.lam is None else False
        self.space = Space(lanes, self.length, self.is_circle_border)  # 道路空间
        self.lane_num = len(lanes)
        # 非车道部分添加墙体对象
        self.__generate_walls()
        if self.is_circle_border:
            self.vehicles = self.vehicle_generator.init_all_vehicles(self)
            for v in self.vehicles:
                self.add_vehicle(v)

    # 运行仿真并获取数据字典
    def get_data_dict(self, time_max):
        self.run(time_max)
        return self.detector.data_processing()

    # 运行仿真
    def run(self, time_max):
        for time in range(time_max):
            # 道路状态更新
            self.update()
            # 检测器检测所有车辆
            self.detector.detect(time, self.vehicles)

    # 运行动画展示
    def show(self, time_max):
        # 创建画布
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # 运行仿真
        for time in range(time_max):
            # 道路状态更新
            self.update()
            # 图像更新
            plt.cla()
            draw(ax, self)
            plt.pause(0.3)
        # 删除画布
        plt.close(fig)

    # 更新所有车辆周围车辆信息
    def update_vehicles_around(self):
        for v in self.vehicles:
            self.get_vehicle_around(v)

    # 所有车辆异步换道（无碰撞的可能）
    def change_lane(self):
        # 更新车辆周围信息
        self.update_vehicles_around()
        # 车辆换道
        for v in self.vehicles:
            # 将车辆从道路空间中清除
            self.space.remove_vehicle(v)
            v.change_lane()
            # 将车辆信息添加到道路空间中
            self.space.add_vehicle(v)

    def update_x(self):
        # 更新车辆周围信息
        self.update_vehicles_around()
        # 更新速度
        for v in self.vehicles:
            v.update_v()
        # 更新位置
        for v in self.vehicles:
            # 将车辆从道路空间中清除
            self.space.remove_vehicle(v)
            v.x = (v.x + v.v * v.direction.value) % self.length
            if not self.is_circle_border:
                # 车辆驶出判断
                if not self._out_road(v):
                    # 将车辆信息添加到道路空间中
                    self.space.add_vehicle(v)

    # 道路状态更新（仿真时间前进一步）
    def update(self):
        if not self.is_circle_border:
            # 开口新车辆到达
            self.__new_vehicle_arrive()
        # 换道
        self.change_lane()
        # 更新位置
        self.update_x()

    # 将车辆对象添加到道路中
    def add_vehicle(self, vehicle):
        if self.is_circle_border:
            self.vehicles.append(vehicle)
            # 去重
            self.vehicles = list(set(self.vehicles))
        vehicle.driving_on = self
        self.space.add_vehicle(vehicle)

    # 将车辆对象从道路中移出
    def remove_vehicle(self, vehicle):
        # 添加时保证vehicles没有重复 就只需要去除一次
        while vehicle in self.vehicles:
            self.vehicles.remove(vehicle)
            self.space.remove_vehicle(vehicle)

    def toString(self):
        for i in range(self.length):
            print(f'{i:3d}', end=' ')
        print('\n______________________________________________________________ ')
        for lane in self.space.index_space:
            for index in lane:
                print(f'{index:3d}', end=' ')
            print(' ')

    '''
    向车辆对象开放的公共接口
    '''

    # 计算车辆密度 veh/km  如果未给出不同种类车辆对veh的换算系数，则单位为 辆/km
    '''
    此时计算为 默认所有车道一样长前提下
    '''

    def get_density(self):
        return (self.vehicle_generator.vehicle_num / self.lane_num) / self.length * 1000

    # 判断车辆是否驶出道路，如果驶出就从道路移出
    def _out_road(self, v):
        """
        :param v: 车辆
        :return: 车辆驶出道路返回True 否则 False
        """
        if v.direction == Direction.right and v.x >= self.length or \
                v.direction == Direction.right and v.x <= 0:
            self.remove_vehicle(v)
            return True
        else:
            return False

    # 获取车辆所在位置的道路类型 车辆不在当前道路 则返回None
    def which_section(self, vehicle):
        if vehicle in self.vehicles:
            return self.space.which_section(vehicle)
        else:
            print('车辆不在当前车道')
            return None

    # 获取传入车辆周围车辆信息
    '''
    向右的车辆其左侧车道 + 1 向左行驶车辆其左侧车道 - 1
    lane = vehicle.lane + vehicle.direction.value
    '''

    def get_front(self, vehicle):
        lr = 'right' if vehicle.direction == Direction.right else 'left'
        vehicle.front = self.space.find_vehicle(vehicle.lane, vehicle, lr,
                                                self.is_circle_border)

    def get_back(self, vehicle):
        lr = 'left' if vehicle.direction == Direction.right else 'right'
        vehicle.back = self.space.find_vehicle(vehicle.lane, vehicle, lr,
                                               self.is_circle_border)

    def get_left_front(self, vehicle):
        lr = 'right' if vehicle.direction == Direction.right else 'left'
        vehicle.left_front = self.space.find_vehicle(vehicle.lane - 1, vehicle, lr,
                                                     self.is_circle_border)

    def get_right_front(self, vehicle):
        lr = 'right' if vehicle.direction == Direction.right else 'left'
        vehicle.right_front = self.space.find_vehicle(vehicle.lane + 1, vehicle, lr,
                                                      self.is_circle_border)

    def get_left_back(self, vehicle):
        lr = 'left' if vehicle.direction == Direction.right else 'right'
        vehicle.left_back = self.space.find_vehicle(vehicle.lane - 1, vehicle, lr,
                                                    self.is_circle_border)

    def get_right_back(self, vehicle):
        lr = 'left' if vehicle.direction == Direction.right else 'right'
        vehicle.right_back = self.space.find_vehicle(vehicle.lane + 1, vehicle, lr,
                                                     self.is_circle_border)

    # 更新车辆所有周围车辆信息
    def get_vehicle_around(self, vehicle):
        self.get_front(vehicle)
        self.get_back(vehicle)
        self.get_right_back(vehicle)
        self.get_right_front(vehicle)
        self.get_left_front(vehicle)
        self.get_left_back(vehicle)

    # 检测当前规则是否会造成撞车
    def has_accident(self):
        for time in range(2000):
            # 开口新车辆到达
            self.__new_vehicle_arrive()
            # 从右向左更新
            self.vehicles.sort(key=lambda x: x.x, reverse=True)
            for v in self.vehicles:
                # 将车辆从道路空间中清除
                self.space.remove_vehicle(v)
                # 车辆换道
                v.change_lane()
                # 计算下一时刻位置
                information = v.information()  # 记录位置更新前信息
                last_time_gap = v.get_gap()
                front = v.front  # 记录更新位置前的前车
                if front is not None and type(front) != Wall:
                    front_information = v.front.information()
                else:
                    front_information = 'Wall'
                v.update_x()
                # 将车辆信息添加到道路空间中
                self.space.add_vehicle(v)
                if last_time_gap + 1 < v.v and type(v) != Wall and front is not None:
                    print('_______________________________')
                    print('发生碰撞前后方车辆信息：')
                    print(information)
                    print('发生碰撞前前方车辆信息：')
                    print(front_information)
                    print('发生碰撞后：')
                    print('碰撞后车：')
                    v.toString()
                    print('碰撞前车：')
                    front.toString()

    # 道路开口有新车到达
    def __new_vehicle_arrive(self):
        for lane in range(self.space.lane_num):
            # 调用车辆生成器当前车道生成车辆
            new_vehicles = self.vehicle_generator.new_vehicle(lane, self)
            for new_vehicle in new_vehicles:
                if new_vehicle is not None:
                    self.add_vehicle(new_vehicle)

    # 向非道路部分添加墙体
    def __generate_walls(self):
        for index, lane in enumerate(self.space.lanes):
            if lane.length < self.length:
                for x in range(lane.length, self.length):
                    wall = Wall(666, index, x, self)
                    self.add_vehicle(wall)


# 车道数据记录类
class Lane:
    def __init__(self, section_length_dict):
        self.section_length_dict = section_length_dict
        self.end_x_section_dict = {}  # {某段末尾位置 ： 类型}
        self.length = 0  # 车道长度
        self.section_length_dict = section_length_dict
        # 更新end_x_section_dict和车道长度
        for vehicle_type in section_length_dict:
            self.length += section_length_dict[vehicle_type]
            self.end_x_section_dict[self.length] = vehicle_type

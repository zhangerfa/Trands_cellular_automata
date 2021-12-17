"""
道路数据结构
道路由车道构成  并对道路上多有车辆状态进行更新
对外提供 run() 方法 运行仿真
"""
from vehicle import Around
from vehicle_enum import Direction
import matplotlib.pyplot as plt
from draw import draw

'''
@:param is_two_way 标记道路上是否包含两个方向行驶车辆
@:param vehicle_generator 车辆生成器，用于在车辆开口生成车辆。当is_two_way为True时，两侧分别生成向左向右的车辆
'''


class Road:
    def __init__(self, lanes, vehicle_generator=None, is_two_way=False):
        self.is_two_way = is_two_way  # 道路上是否允许
        self.vehicles = []  # 道路上所有车辆对象列表
        self.vehicle_generator = vehicle_generator  # 车辆生成器
        self.space = Space(lanes)  # 道路空间
        self.length = max([x.length for x in lanes])  # 最大车道长度为道路长度

    # 运行仿真
    def run(self, time_max):
        for time in range(time_max):
            # 道路状态更新
            self.update()

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
            plt.pause(0.1)
        # 删除画布
        plt.close(fig)

    # 道路状态更新（仿真时间前进一步）
    def update(self):
        # 开口新车辆到达
        self.__new_vehicle_arrive()
        # 所有车辆异步换道（防止碰撞）
        for v in self.vehicles:
            # 将车辆从道路空间中清除
            self.space.remove_vehicle(v)
            # 车辆换道
            v.change_lane()
            # 计算下一时刻位置
            v.update_x()
            # 将车辆信息添加到道路空间中
            self.space.add_vehicle(v)

    # 将车辆对象添加到道路中
    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        self.space.add_vehicle(vehicle)

    def toString(self):
        for i in range(self.length):
            print(f'{i:3d}', end=' ')
        print('______________________________________________________________ ')
        for lane in self.space.index_space:
            for index in lane:
                print(f'{index:3d}', end=' ')
            print(' ')

    '''
    向车辆对象开放的公共接口
    '''

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
    def get_vehicle_around(self, vehicle):
        around_dict = {}
        for item in vehicle.around_list:
            if item == Around.front:
                lane = vehicle.lane
                flag = 'right' if vehicle.direction == Direction.right else 'left'
            elif item == Around.back:
                lane = vehicle.lane
                flag = 'left' if vehicle.direction == Direction.right else 'right'
            elif item == Around.left_front:
                lane = vehicle.lane + vehicle.direction.value
                flag = 'right' if vehicle.direction == Direction.right else 'left'
            elif item == Around.right_front:
                lane = vehicle.lane - vehicle.direction.value
                flag = 'right' if vehicle.direction == Direction.right else 'left'
            elif item == Around.left_back:
                lane = vehicle.lane + vehicle.direction.value
                flag = 'left' if vehicle.direction == Direction.right else 'right'
            elif item == Around.right_back:
                lane = vehicle.lane - vehicle.direction.value
                flag = 'left' if vehicle.direction == Direction.right else 'right'
            else:
                print('vehicle.around_dict 错误')
            around_dict[item] = self.space.find_vehicle(lane, vehicle, flag)
        return around_dict

    # 道路开口有新车到达
    def __new_vehicle_arrive(self):
        for lane in range(self.space.lane_num):
            # 当前车道生成向右车辆
            new_vehicle = self.vehicle_generator.new_vehicle(lane, self)
            if new_vehicle is not None:
                self.add_vehicle(new_vehicle)
            if self.is_two_way:
                # 当前车道生成向左车辆
                new_vehicle = self.vehicle_generator.new_vehicle(lane, self, Direction.left)
                if new_vehicle is not None:
                    self.add_vehicle(new_vehicle)


# 空间类（矩形空间）
class Space:
    def __init__(self, lanes):
        self.space = []  # 存储道路离散空间 无车 None 有车 对象引用
        self.index_space = []  # 存储道路离散空间 无车 0 有车 车id
        self.lanes = lanes  # 车道对象列表
        self.lane_num = len(lanes)  # 车道数
        # 初始化 space index_space
        for lane in lanes:
            self.space.append([0] * lane.length)
            self.index_space.append([0] * lane.length)

    # 将车辆从space中移出
    def remove_vehicle(self, vehicle):
        space_range = vehicle.get_space_range()
        values = [0, 0]
        self.__update(space_range, values)

    # 将车辆添加到space中
    def add_vehicle(self, vehicle):
        space_range = vehicle.get_space_range()
        values = [vehicle, vehicle.index]
        self.__update(space_range, values)

    # 寻找车辆在某一车道的的右侧车辆 或 左侧车（由flag区分）
    def find_vehicle(self, lane, vehicle, flag):
        # 如果输入车道不合法 返回None (对应寻找 0 车道左车等情况)
        if lane < 0 or lane >= self.lane_num:
            return None
        lane_length = self.lanes[lane].length
        if flag == 'right':
            if vehicle.direction == Direction.right:
                start_x = min(vehicle.x + 1, lane_length)
            else:
                start_x = max(vehicle.x + vehicle.length, 0)
            find_range = range(start_x, lane_length - 1)
        elif flag == 'left':
            if vehicle.direction == Direction.right:
                start_x = min(max(vehicle.x - vehicle.length, 0), lane_length- 1)
            else:
                start_x = min(max(vehicle.x - 1, 0), lane_length - 1)
            find_range = range(start_x, -1, -1)
        else:
            print('flag输入有误')
            return
        for x in find_range:
            if self.space[lane][x] != 0:
                if self.space[lane][x] != vehicle:
                    return self.space[lane][x]
        return None

    # 获取车辆所在位置的道路类型
    def which_section(self, vehicle):
        end_x_ls = [x for x in self.lanes[vehicle.lane].end_x_section_dict.keys()]
        for end_x in end_x_ls:
            if end_x > vehicle.x:
                return self.lanes[vehicle.lane].end_x_section_dict[end_x]

    # 更新space矩阵 将传入范围改为该值
    '''
    @:param space_range : 需要更新的范围 [[lane, x], [lane, x], ...]
    @:param values : 更新的值 [vehicle, vehicle_index] or [0, 0]
    '''

    def __update(self, space_range, values):
        for position in space_range:
            lane = position[0]
            x = position[1]
            if 0 <= lane < self.lane_num and 0 <= x < self.lanes[lane].length:
                self.space[lane][x] = values[0]
                self.index_space[lane][x] = values[1]


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


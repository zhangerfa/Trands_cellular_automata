"""
道路数据结构
道路由车道构成  并对道路上多有车辆状态进行更新
对外提供 run() 方法 运行仿真
"""
from vehicle import Around


class Road:
    def __init__(self, lanes, vehicle_generator):
        self.vehicles = []  # 道路上所有车辆对象列表
        self.vehicle_generator = vehicle_generator  # 车辆生成器
        self.lanes = lanes  # 车道对象列表
        self.lane_num = len(lanes)  # 车道数
        self.space = []  # 存储道路离散空间 无车 None 有车 对象引用
        self.index_space = []  # 存储道路离散空间 无车 0 有车 车id
        self.length = max([x.length for x in lanes]) # 最大车道长度为道路长度
        # 初始化 space index_space
        for lane in self.lanes:
            self.space.append([0] * lane.length)
            self.index_space.append([0] * lane.length)

    # 运行仿真
    def run(self, time_max):
        for time in range(time_max):
            # 道路状态更新
            self.update()

    # 道路状态更新（仿真时间前进一步）
    def update(self):
        # 开口新车辆到达
        self.__new_vehicle_arrive()
        # 所有车辆异步换道（防止碰撞）
        for v in self.vehicles:
            # 清除space中的车辆信息
            self.__remove_vehicle(v)
            # 车辆换道
            v.change_lane()
            # 将车辆信息添加到space中
            self.__add_vehicle(v)
        # 所有车辆同步前进（面向同一交通环境）
        for v in self.vehicles:
            v.update_x()
        # 所有车辆位置更新完后更新space
        for v in self.vehicles:
            # 清除space中的车辆信息
            self.__remove_vehicle(v)
            # 将车辆信息添加到space中
            self.__add_vehicle(v)

    '''
    向车辆对象开放的公共接口
    '''
    # 获取车辆所在位置的道路类型 车辆不在当前道路 则返回None
    def which_section(self, vehicle):
        if vehicle in self.vehicles:
            end_x_ls = [x for x in self.lanes[vehicle.lane].end_x_section_dict.keys()]
            for end_x in end_x_ls:
                if end_x > vehicle.x:
                    return self.lanes[vehicle.lane].end_x_section_dict[end_x]
        else:
            print('车辆不在当前车道')
            return None

    # 获取传入车辆周围车辆信息
    def get_vehicle_around(self, vehicle):
        around_dict = {}
        for item in vehicle.around_list:
            if item == Around.front:
                around_dict[item] = self.__find_vehicle(vehicle.lane, vehicle, 'front')
            if item == Around.back:
                around_dict[item] = self.__find_vehicle(vehicle.lane, vehicle, 'back')
            if item == Around.left_front:
                around_dict[item] = self.__find_vehicle(vehicle.lane + 1, vehicle, 'front')
            if item == Around.right_front:
                around_dict[item] = self.__find_vehicle(vehicle.lane - 1, vehicle, 'front')
            if item == Around.left_back:
                around_dict[item] = self.__find_vehicle(vehicle.lane + 1, vehicle, 'back')
            if item == Around.right_back:
                around_dict[item] = self.__find_vehicle(vehicle.lane - 1, vehicle, 'back')
        return around_dict

    '''
    私有方法
    '''
    # 清除space中的车辆信息
    def __remove_vehicle(self, vehicle):
        space_range = vehicle.get_space_range()
        values = [0, 0]
        self.__update_space(space_range, values)

    # 将车辆信息添加到space中
    def __add_vehicle(self, vehicle):
        space_range = vehicle.get_space_range()
        values = [vehicle, vehicle.index]
        self.__update_space(space_range, values)

    # 新车到达
    def __new_vehicle_arrive(self):
        for lane in range(self.lane_num):
            # 当前车道生成车辆
            new_vehicle = self.vehicle_generator.new_vehicle(lane, self)
            if new_vehicle is not None:
                self.vehicles.append(new_vehicle)

    # 更新space矩阵 将传入范围改为该值
    '''
    @:param space_range : 需要更新的范围 [[lane, x], [lane, x], ...]
    @:param values : 更新的值 [vehicle, vehicle_index] or [0, 0]
    '''

    def __update_space(self, space_range, values):
        for position in space_range:
            lane = position[0]
            x = position[1]
            if 1 <= lane >= self.lane_num and x < self.lanes[lane].length:
                self.space[lane][x] = values[1]
                self.space[lane][x] = values[2]

    # 寻找车辆在某一车道的的前车 或 后车（由flag区分）
    def __find_vehicle(self, lane, vehicle, flag):
        # 如果输入车道不合法 返回None (对应寻找 0 车道左车等情况)
        if lane < 0 or lane >= self.lane_num:
            return None
        if flag == 'front':
            lane_length = self.lanes[lane].length
            find_range = range(min(vehicle.x + 1, lane_length - 1), lane_length - 1)
        elif flag == 'back':
            find_range = range(max(vehicle.x - vehicle.length, 0), -1, -1)
        else:
            print('flag输入有误')
            return
        for x in find_range:
            if self.space[lane][x] != 0:
                return self.space[lane][x]
        return None


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

from src.vehicle_enum import Direction


# 空间类（矩形空间）
class Space:
    def __init__(self, lanes, road_length, is_circle_border):
        self.length = road_length  # 空间长度
        self.space = []  # 存储道路离散空间 无车 None 有车 对象引用
        self.index_space = []  # 存储道路离散空间 无车 0 有车 车id
        self.lanes = lanes  # 车道对象列表
        self.lane_num = len(lanes)  # 车道数
        self.is_circle_border = is_circle_border  # 是否为周期边界条件
        # 初始化 space index_space
        for i, lane in enumerate(lanes):
            cur_lane = []
            cur_lane += [0] * lane.length
            if lane.length < road_length:
                # 非道路空间以 None 填充
                cur_lane += [None] * (road_length - lane.length)
            self.space.append(cur_lane.copy())
            cur_lane.clear()
            cur_lane += [0] * lane.length
            if lane.length < road_length:
                # 非道路空间 index 为-1
                cur_lane += [-1] * (road_length - lane.length)
            self.index_space.append(cur_lane.copy())

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
    def find_vehicle(self, lane, vehicle, flag, is_circle_border):
        # 如果输入车道不合法 返回None (如寻找 0 车道左车等情况)
        if lane < 0 or lane >= self.lane_num:
            return None
        lane_length = len(self.space[lane])
        if flag == 'right':
            if is_circle_border:
                if vehicle.direction == Direction.right:
                    find_range = range(vehicle.x + 1, 2 * lane_length)
                else:
                    find_range = range(vehicle.x + vehicle.length, 2 * lane_length)
            else:
                if vehicle.direction == Direction.right:
                    start_x = min(vehicle.x + 1, self.length)
                else:
                    start_x = max(vehicle.x + vehicle.length, 0)
                find_range = range(start_x, self.length - 1)
        elif flag == 'left':
            if is_circle_border:
                if vehicle.direction == Direction.right:
                    start_x = vehicle.x - vehicle.length + lane_length
                else:
                    start_x = vehicle.x - 1 + lane_length
            else:
                if vehicle.direction == Direction.right:
                    start_x = min(max(vehicle.x - vehicle.length, 0), self.length - 1)
                else:
                    start_x = min(max(vehicle.x - 1, 0), self.length - 1)
            find_range = range(start_x, -1, -1)
        else:
            print('flag输入有误')
            return
        min_gap = float('inf')
        space = []
        if is_circle_border:
            for i in self.space:
                space.append(i * 2)
        else:
            space = self.space
        front = None
        for cur_lane in range(vehicle.lane, vehicle.lane + vehicle.width):
            for x in find_range:
                if space[lane][x] != 0 and space[lane][x] != vehicle:
                    cur_gap = abs(x - vehicle.x)
                    if cur_gap < min_gap:
                        front = space[lane][x]
                    break
        return front

    # 获取车辆所在位置的道路类型
    def which_section(self, vehicle):
        end_x_list = self.get_section_end_x_list(vehicle.lane)
        for end_x in end_x_list:
            if end_x > vehicle.x:
                return self.lanes[vehicle.lane].end_x_section_dict[end_x]

    # 判断输入车辆在传入方向旁边是否有车
    def has_next_to(self, vehicle, direction):
        lane = vehicle.lane - vehicle.direction.value * direction.value
        x = vehicle.x
        space_range = self.get_range([lane, x], vehicle.length, vehicle.width, vehicle.direction)
        for position in space_range:
            if self.is_position_legal(position):
                lane = position[0]
                x = position[1]
                if self.space[lane][x] not in [0, vehicle]:
                    return True
        return True

    # 判断坐标是否合法
    def is_position_legal(self, position):
        lane = position[0]
        x = position[1]
        if not 0 <= lane < self.lane_num:
            return False
        if not 0 <= x < self.length:
            return False
        return True

    # 获取传入坐标、长宽、方向的车辆所占的空间
    def get_range(self, position, length, width, direction):
        lane = position[0]
        x = position[1]
        space_range = []  # 车辆所在所有元胞的坐标
        for delta_x in range(length):
            for delta_lane in range(width):
                cur_lane = lane - delta_lane
                cur_x = x - delta_x * direction.value
                if self.is_circle_border:
                    cur_x = cur_x % self.lanes[lane].length
                space_range.append([cur_lane, cur_x])
        return space_range

    # 更新space矩阵 将传入范围改为该值
    '''
    @:param space_range : 需要更新的范围 [[lane, x], [lane, x], ...]
    @:param values : 更新的值 [vehicle, vehicle_index] or [0, 0]
    '''

    def __update(self, space_range, values):
        for position in space_range:
            lane = position[0]
            x = position[1]
            # 判断坐标是否在空间范围内
            if 0 <= lane < self.lane_num and 0 <= x < self.length:
                self.space[lane][x] = values[0]
                self.index_space[lane][x] = values[1]

    # 返回输入车道各部分的end_x list
    def get_section_end_x_list(self, lane):
        return list(self.lanes[lane].end_x_section_dict.keys())

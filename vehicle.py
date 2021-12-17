'''
车辆数据结构
车辆坐标为其最前方（前进方向）元胞坐标
所有长度单位为元胞（3.75 * 3.75）
'''
from vehicle_enum import Direction, Around


class Vehicle:

    def __init__(self, index, lane, x, road, direction=Direction.right):
        self.direction = direction  # 车辆前进方向 默认向右
        self.index = index  # int 用于唯一标识车辆
        self.x = x  # 车道方向位置 车头所在元胞位置
        self.v = 0  # 车辆车速
        self.lane = lane  # 车辆位于车道
        self.driving_on = road  # 车辆行驶于该道路对象
        self.length = 1  # 车辆长度
        self.width = 1  # 车辆宽度
        self.front = None  # 前车
        self.back = None  # 后车
        self.left_front = None  # 左前车
        self.right_front = None  # 右前车
        self.left_back = None  # 左后车
        self.right_back = None  # 右后车
        # 需要维护的车辆周围车辆信息列表
        self.around_list = [Around.front, Around.back, Around.left_front, Around.left_back,
                            Around.right_front, Around.right_back]

    # 更新位置
    def update_x(self):
        # 更新车辆周围信息
        self.__update_around()
        # 更新速度
        self._update_v()
        # 更新车辆位置
        self.x += self.v * self.direction.value

    # 车辆换道：找到目标车道，并试试换道
    def change_lane(self):
        # 更新车辆周围信息
        self.__update_around()
        # 判断是否需要换道
        if self._need_change_lane():
            # 遍历换道方向(当前车道+1 -1) 直到换道 或 所有方向无法换道
            for direction in Direction:
                if self._can_change_lane(direction):
                    desire_lane = self.lane + direction.value
                    self.lane = desire_lane
                    return

    # 获取车辆所在所有元胞的坐标  （越界值也会返回）
    def get_space_range(self):
        space_range = []  # 车辆所在所有元胞的坐标
        for delta_x in range(self.length):
            for delta_lane in range(self.width):
                cur_lane = self.lane - delta_lane
                cur_x = self.x - delta_x * self.direction.value
                space_range.append([cur_lane, cur_x])
        return space_range

    def toString(self):
        self.__update_around()
        out = f'id: {self.index},{type(self)}, lane: {self.lane},' + \
              f'x: {self.x}, v: {self.v}, 方向: {self.direction}\n'
        if self.front is not None:
            out += f' 前车：{self.front.index}'
        else:
            out += f' 无前车 '
        if self.back is not None:
            out += f' 后车：{self.back.index}'
        else:
            out += f' 无后车 '
        if self.left_front is not None:
            out += f' 左前车：{self.left_front.index}'
        else:
            out += f' 无左前车 '
        if self.left_back is not None:
            out += f' 左后车：{self.left_back.index}'
        else:
            out += f' 无左后车 '
        if self.right_back is not None:
            out += f' 右后车：{self.right_back.index}'
        else:
            out += f' 无右后车 '
        out += f'\n前车距： {self.get_gap()} 后车距：{self.get_gap_back()} 左前车距： {self.get_gap_left()} 右前车距：{self.get_gap_right()} 左后车距： {self.get_gap_back_left()} 右后距：{self.get_gap_back_right()}'

        print(out)

    '''
    需要被子类重写的方法
    '''
    # 更新车速 子类实现 写为接口
    def _update_v(self):
        self.v = 5

    # 判断是否需要换道
    def _need_change_lane(self):
        pass

    # 判断能否向传入方向换道
    def _can_change_lane(self, direction):
        pass

    '''
    无需子类重写的方法
    '''
    # 更新车辆周围信息
    def __update_around(self):
        around_dict = self.driving_on.get_vehicle_around(self)
        # 将返回周围车辆信息赋值给车辆
        for item in around_dict:
            v = around_dict[item]
            if item == Around.front:
                self.front = v
            if item == Around.back:
                self.back = v
            if item == Around.left_front:
                self.left_front = v
            if item == Around.right_front:
                self.right_front = v
            if item == Around.left_back:
                self.left_back = v
            if item == Around.right_back:
                self.right_back = v

    # 获取前车距
    def get_gap(self):
        if self.front is None:
            return float('inf')
        else:
            return get_distance(self, self.front)

    # 获取后车距
    def get_gap_back(self):
        if self.back is None:
            return float('inf')
        else:
            return get_distance(self, self.back)

    # 获取左前车距
    def get_gap_left(self):
        if self.left_front is None:
            return float('inf')
        else:
            return get_distance(self, self.left_front)

    # 获取右前车距
    def get_gap_right(self):
        if self.right_front is None:
            return float('inf')
        else:
            return get_distance(self, self.right_front)

    # 获取左后车距
    def get_gap_back_left(self):
        if self.left_back is None:
            return float('inf')
        else:
            return get_distance(self, self.left_back)

    # 获取右后车距
    def get_gap_back_right(self):
        if self.right_back is None:
            return float('inf')
        else:
            return get_distance(self, self.right_back)


# 计算两辆车之间的前车距
def get_distance(v1, v2):
    # v1.x ≥ v2.x
    v1, v2 = (v2, v1) if v1.x <= v2.x else (v1, v2)
    if v1.direction == v2.direction:
        # 同向: 间距 = 大 - 小 - 前车（前进方向）车长
        v = v1 if v1.direction == Direction.right else v2
        return v1.x - v2.x - v.length
    else:
        if v1.direction == Direction.left:
            # x小的车向左 对向 只会是求 前车距
            # 对向: 前车距 = 大 - 小 - 1
            return v1.x - v2.x - 1
        if v1.direction == Direction.right:
            # x大的车向右 对向 只会是求 后车距
            # 对向： 后车距 = 大 - 小 + 1 - 两车车长
            return v1.x - v2.x + 1 - v1.length - v2.length

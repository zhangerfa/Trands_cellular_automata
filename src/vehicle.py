"""
车辆数据结构
车辆坐标为其最前方（前进方向）元胞坐标
所有长度单位为元胞（3.75 * 3.75）
"""
from src.vehicle_enum import Direction, Color


class Vehicle:
    length = 1  # 车辆长度
    width = 1  # 车辆宽度

    def __init__(self, index, lane, x, road=None, direction=Direction.right):
        self.direction = direction  # 车辆前进方向 默认向右
        self.index = index  # int 用于唯一标识车辆
        self.x = x  # 车道方向位置 车头所在元胞位置
        self.v = 0  # 车辆车速
        self.lane = lane  # 车辆位于车道
        self.driving_on = road  # 车辆行驶于该道路对象
        self.front = None  # 前车
        self.back = None  # 后车
        self.left_front = None  # 左前车
        self.right_front = None  # 右前车
        self.left_back = None  # 左后车
        self.right_back = None  # 右后车

    # 车辆换道：找到目标车道，并试试换道
    def change_lane(self):
        # 判断是否需要换道
        if self._need_change_lane():
            # 遍历换道方向(当前车道+1 -1) 直到换道 或 所有方向无法换道
            for direction in Direction:
                if self._can_change_lane(direction):
                    self.update_lane(direction)
                    return

    # 获取车辆所在所有元胞的坐标  （越界值也会返回）
    def get_space_range(self):
        return self.driving_on.space.get_range([self.lane, self.x], self.length, self.width, self.direction)

    def toString(self):
        out = self.information()
        print(out)

    def information(self):
        self.driving_on.update_vehicles_around()
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
        out += f'\n前车距： {self.get_gap()} 后车距：{self.get_gap_back()} 左前车距： ' \
               f'{self.get_gap_left()} 右前车距：{self.get_gap_right()} 左后车距： ' \
               f'{self.get_gap_back_left()} 右后距：{self.get_gap_back_right()}'
        return out

    '''
    需要被子类重写的方法
    '''

    # 更新车速 子类实现 写为接口
    def update_v(self):
        pass

    # 判断是否需要换道 默认无需换道
    def _need_change_lane(self):
        return False

    # 判断能否向传入方向换道 默认不能换道
    def _can_change_lane(self, direction):
        return False

    # 实施换道
    def update_lane(self, direction):
        # 向右行驶车辆向右（前进方向）换道lane - 1
        # 向右行驶车辆向右（前进方向）换道lane + 1
        self.lane -= self.direction.value * direction.value

    '''
    无需子类重写的方法
    '''

    # 获取前车距
    def get_gap(self):
        if self.front is None:
            return float('inf')
        else:
            return max(get_distance(self, self.front), 0)

    # 获取后车距
    def get_gap_back(self):
        if self.back is None:
            return float('inf')
        else:
            return max(get_distance(self, self.back), 0)

    # 获取左前车距
    def get_gap_left(self):
        if self.left_front is None:
            return float('inf')
        else:
            return max(get_distance(self, self.left_front), 0)

    # 获取右前车距
    def get_gap_right(self):
        if self.right_front is None:
            return float('inf')
        else:
            return max(get_distance(self, self.right_front), 0)

    # 获取左后车距
    def get_gap_back_left(self):
        if self.left_back is None:
            return float('inf')
        else:
            return max(get_distance(self, self.left_back), 0)

    # 获取右后车距
    def get_gap_back_right(self):
        if self.right_back is None:
            return float('inf')
        else:
            return max(get_distance(self, self.right_back), 0)

    # 获取车辆目前所在的车道部分
    def get_section(self):
        return self.driving_on.which_section(self)

    def get_lane_length(self):
        return self.driving_on.space.lanes[self.lane].length

    # 判断传入方向是否有车
    def has_next_to(self, direction):
        return self.driving_on.space.has_next_to(self, direction)


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


# 墙体类
class Wall(Vehicle):
    color = Color.black

    # 墙体永远不会移动， 且会阻碍车辆移动
    def update_v(self):
        self.v = 0

'''
车辆数据结构
车辆坐标为其最前方（前进方向）元胞坐标
所有长度单位为元胞（3.75 * 3.75）
'''

from enum import Enum


# 方向类
class Direction:
    right = -1
    left = 1


# 车辆颜色枚举类
class Color(Enum):
    red = [1, 0, 0]
    blue = [0, 0, 1]
    green = [0, 1, 0]
    black = [0, 0, 0]


# 周围车辆枚举类
class Around(Enum):
    front = 'front'
    back = 'back'
    left_front = 'left_front'
    right_front = 'right_front'
    left_back = 'left_back'
    right_back = 'right_back'


class Vehicle:

    def __init__(self, index, lane, x, road):
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
        self.x += self.v

    # 车辆换道：找到目标车道，并试试换道
    def change_lane(self):
        # 更新车辆周围信息
        self.__update_around()
        # 判断是否需要换道
        if self._need_change_lane():
            # 遍历换道方向 直到换道 或 所有方向无法换道
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
                cur_x = self.x - delta_x
                space_range.append([cur_lane, cur_x])
        return space_range

    def toString(self):
        out = f'id:{self.index},{type(self)},lane:{self.lane},' + \
              f'x:{self.x},v:{self.v}\n'
        if self.front is not None:
            out += f' 前车：{self.front.id}'
        else:
            out += f' 无前车 '
        return out

    ### 需要被子类重写的方法
    # 更新车速 子类实现 写为接口
    def _update_v(self):
        self.v = 5

    # 判断是否需要换道
    def _need_change_lane(self):
        pass

    # 判断能否向传入方向换道
    def _can_change_lane(self, direction):
        pass

    ### 无需子类重写的方法
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
    def _get_gap(self):
        if self.front is None:
            return float('inf')
        return self.front.x - self.x - self.front.length

    # 获取左前车距
    def _get_gap_left(self):
        if self.left_front is None:
            return float('inf')
        return self.left_front.x - self.x - self.left_front.length

    # 获取右前车距
    def _get_gap_right(self):
        if self.right_front is None:
            return float('inf')
        return self.right_front.x - self.x - self.right_front.length

    # 获取左后车距
    def _get_gap_back_left(self):
        if self.left_back is None:
            return float('inf')
        return self.left_back.x - self.x - self.left_back.length

    # 获取右后车距
    def _get_gap_back_right(self):
        if self.right_back is None:
            return float('inf')
        return self.right_back.x - self.x - self.right_back.length

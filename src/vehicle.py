from src.vehicle_enum import Direction

"""
车辆类封装仿真时车辆跟驰、换道的运算规则
提供获取车辆跟驰、换道时所需的信息：前车距、后车距、左前车距、右前车距、左后车距、右后车距、车道类型
"""


class Vehicle:
    length = 1  # 车辆长度
    width = 1  # 车辆宽度
    # 车辆周围车辆：前 后 左前 右前 左后 右后
    around = {"front": None,
              "back": None,
              "left_front": None,
              "right_front": None,
              "left_back": None,
              "right_back": None}

    def __init__(self, index, lane, x, direction=Direction.right):
        self.direction = direction  # 车辆前进方向 默认向右
        self.index = index  # int 用于唯一标识车辆
        self.x = x  # 车道方向位置 车头所在元胞位置
        self.v = 0  # 车辆车速
        self.lane = lane  # 车辆所在车道对象

    # 车辆换道：找到目标车道，并尝试换道，返回实际换道方向
    def change_lane(self):
        # 判断是否需要换道
        if self.need_change_lane():
            # 遍历换道方向(当前车道+1 -1) 直到换道 或 所有方向无法换道
            for direction in Direction:
                if self.can_change_lane(direction):
                    self.__update_lane(direction)
                    return direction

    # 实施换道
    def __update_lane(self, direction):
        # 向右行驶车辆向右（前进方向）换道lane - 1
        # 向右行驶车辆向右（前进方向）换道lane + 1
        self.lane -= self.direction.value * direction.value

    '''
    需要被子类重写的方法
    '''

    # 更新车速 子类实现 写为接口
    def update_v(self):
        pass

    # 判断是否需要换道 默认无需换道
    def need_change_lane(self):
        return False

    # 判断能否向传入方向换道 默认不能换道
    def can_change_lane(self, direction):
        return False

    '''
    为跟驰、换道提供的方法
    '''

    # 获取前车距
    def get_front_gap(self):
        return self.__get_gap("front")

    # 获取后车距
    def get_back_gap(self):
        return self.__get_gap("back")

    # 获取左前车距
    def get_left_front_gap(self):
        return self.__get_gap("left_front")

    # 获取右前车距
    def get_right_front_gap(self):
        self.__get_gap("right_front")

    # 获取左后车距
    def get_gap_back_left(self):
        return self.__get_gap("left_back")

    # 获取右后车距
    def get_gap_back_right(self):
        self.__get_gap("right_back")

    # 获取车辆目前所在的车道类型
    def get_section_type(self):
        return self.lane.which_section(self)

    # 判断传入方向是否有车
    def has_next_to(self, direction):
        pass

    # 获取指定车距，传入车辆类型：前车距、后车距、左前车距、右前车距、左后车距、右后车距
    def __get_gap(self, gap_type):
        vehicle = self.around[gap_type]
        if vehicle is None:
            return float('inf')
        else:
            return max(get_distance(self, vehicle), 0)


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

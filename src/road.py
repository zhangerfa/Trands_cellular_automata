"""
Road类包含若干Lane对象，提供更新车辆所在车道和车辆周围车辆的方法
@:param lanes Lane对象列表
"""


class Road:
    def __init__(self, lanes):
        self.lanes = lanes
        self.length = max([x.length for x in lanes])  # 最大车道长度为道路长度
        self.lane_num = len(lanes)

    # 换道时更新车辆所在车道，传入车辆对象和换道方向
    def update_lane(self, vehicle, direction):
        pass

    # 车辆跟驰、换道时更新车辆周围车辆信息
    # direction为换道方向，如果为空则表示车辆要进行跟驰
    def update_around(self, vehicle, direction):
        pass

    # 获取传入车辆周围车辆信息
    '''
    向右的车辆其左侧车道 + 1 向左行驶车辆其左侧车道 - 1
    lane = vehicle.lane + vehicle.direction.value
    '''


# 车道数据记录类
# 一个车道可由多种类型的道路组成
# 提供查询车辆所在位置的道路类型的方法
class Lane:
    def __init__(self, section_length_dict):
        self.section_length_dict = section_length_dict
        self.end_x_section_dict = {}  # {末尾位置 ： 类型}
        self.length = 0  # 车道长度
        self.section_length_dict = section_length_dict
        # 更新end_x_section_dict和车道长度
        for vehicle_type in section_length_dict:
            self.length += section_length_dict[vehicle_type]
            self.end_x_section_dict[self.length] = vehicle_type

    # 查询车辆所在位置的道路类型
    def which_section(self, vehicle):
        if vehicle.x > self.length:
            print('在使用Lane.which_section()时，车辆位置超出车道长度')
            return None
        for end_x in self.end_x_section_dict:
            if vehicle.x <= end_x:
                return self.end_x_section_dict[end_x]

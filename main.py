import random
from road import *
from vehicle_generator import Vehicle_generator
from vehicle import Vehicle
from enum import Enum
from vehicle_enum import Color
from detector import Detector
import xlwt


#### 创建仿真使用的车辆类
# 小汽车类
class Car(Vehicle):
    a_max = 4  # 最大加速度
    color = Color.red  # 车辆颜色
    v_max = 7  # 最大速度
    gap_desire = 12  # 期望前车距
    p = 0.2  # 随机慢化概率
    p2 = 0.35  # M1段车道3处随机慢化概率
    length = 2  # 车辆长度

    # 更新车速
    def _update_v(self):
        gap = max(self.get_gap(), 0)
        # 车辆在M1段
        section = self.get_section()
        if section == Section.M1:
            self.v = min(self.v + 1, self.v_max, gap)
        else:
            self.v = min(self.v + 2, self.v_max, gap)

    # 判断能否向传入方向换道
    def _can_change_lane(self, direction):
        '''
        目标车道前车距 ＞ 当前车道前车距 且 目标车道后车距 ＞ 最大车速
        :param direction: 换道方向 为 Direction枚举类对向
        :return: 能否向传入方向换道
        '''
        gap = self.get_gap()  # 前车距
        if direction == Direction.right:
            if self.lane == 0:
                return False
            gap_desire_front = self.get_gap_right()  # 右前车距
            gap_desire_back = self.get_gap_back_right()  # 右后车距
        else:
            if self.lane == self.driving_on.lane_num - 1:
                return False
            gap_desire_front = self.get_gap_left()  # 左前车距
            gap_desire_back = self.get_gap_back_left()  # 左后车距
        if gap_desire_front > gap and gap_desire_back > self.v_max:
            return True
        else:
            return False

    # 判断是否需要换道
    def _need_change_lane(self):
        '''
        如果前车距 ＜ 最大车速 则换道
        :return: 是否换道
        '''
        gap = self.get_gap()  # 前车距
        if gap < self.v_max:
            return True
        else:
            return False


# 货车类
class Truck(Car):
    a_max = 2  # 最大加速度
    color = Color.blue  # 车辆颜色
    v_max = 5  # 最大速度
    gap_desire = 12  # 期望前车距
    p = 0.3  # 随机慢化概率
    length = 4


#### 构建测试场景
# 创建车道类型
class Section(Enum):
    M0 = '战场路段'
    M1 = '缩减路段'
    M2 = '施工路段'


# 创建检测器(基础检测器可以检测道路流量、平均车速)
class MyDector(Detector):

    # 将新增检测数据添加到监测数据字典{数据名称: 默认值}
    def __init__(self, time_range, space_range):
        super().__init__(time_range, space_range)
        self.vehicles_data['change_lane_times'] = 0

    def start_detect_event(self, vehicle):
        super(MyDector, self).start_detect_event(vehicle)
        # 第一次检测到车辆时记录车辆换道次数
        self.detecing_vehicles_df.loc[vehicle.index, 'change_lane_times'] = vehicle.change_lane_times

    def finish_detect_event(self, vehicle):
        super(MyDector, self).finish_detect_event(vehicle)
        # 最后一次检测到车辆时计算在检测路段的换道次数
        start_times = self.detecing_vehicles_df.loc[vehicle.index, 'change_lane_times']
        self.detecing_vehicles_df.loc[vehicle.index, 'change_lane_times'] = vehicle.change_lane_times - start_times

    def data_processing(self):
        out_dict = super(MyDector, self).data_processing()
        # 计算平均换道次数
        out_dict['change_lane_times'] = self.completed_vehicles_df.loc[:, 'change_lane_times'].mean()
        return out_dict


def show():
    # 创建车辆生成器
    lam = 0.4  # 到达率
    vehicle_generator = Vehicle_generator({Car: 0.5, Truck: 0.5}, lam)

    # 创建车道对象
    L1 = Lane({Section.M0: 100, Section.M1: 50, Section.M2: 50})
    L2 = Lane({Section.M0: 100, Section.M1: 50, Section.M2: 50})
    L3 = Lane({Section.M0: 100, Section.M1: 50})
    lanes = [L1, L2, L3]

    time_max = 200
    time_range = [100, time_max]
    space_range = [100, 150]
    detector = MyDector(time_range, space_range)

    # 创建道路
    road = Road(lanes, vehicle_generator, detector)

    # 展示仿真动画
    road.show(time_max)
    # 检测当前规则是否会发生碰撞
    road.has_accident()


#### 运行仿真

def generate_data():
    # 将数据写入excel
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('sheet1')
    path = r'.\data.xls'
    # 写入列名
    sheet.write(0, 0, 'car_percent')
    sheet.write(0, 1, 'M1_length')
    sheet.write(0, 2, 'capacity')
    sheet.write(0, 3, 'average_speed')
    sheet.write(0, 4, 'change_lane_frequency')
    row = 1

    for M1_length in range(8, 2, 48):
        # 创建车道对象
        L1 = Lane({Section.M0: 100, Section.M1: M1_length, Section.M2: 50})
        L2 = Lane({Section.M0: 100, Section.M1: M1_length, Section.M2: 50})
        L3 = Lane({Section.M0: 100, Section.M1: M1_length})
        lanes = [L1, L2, L3]
        # 车辆占比变化
        for i in range(10):
            car_percent = i / 10
            truck_percent = 1 - car_percent
            # 创建车辆生成器
            lam = 0.4  # 到达率
            vehicle_generator = Vehicle_generator({Car: car_percent, Truck: truck_percent}, lam)
            # 创建检测器
            time_max = 5000
            time_range = [1000, time_max]
            space_range = [100, 100 + M1_length]
            detector = MyDector(time_range, space_range)
            # 创建道路
            road = Road(lanes, vehicle_generator, detector)
            # 跑数据
            road.run(time_max)
            data_dict = road.detector.data_processing()
            # 写入数据
            sheet.write(row, 0, car_percent)
            sheet.write(row, 1, M1_length)
            write_data(path, data_dict, row)
            row += 1
            # 保存在path 中
            workbook.save(path)
            print(f'小汽车占比：{car_percent}，M1长度:{M1_length}的数据已保存')

show()

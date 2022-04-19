import pandas as pd
from src.vehicle import Wall
'''
检测器类——可以检测检测路段某位断面流量和平均车速
如果需要检测其他数据请继承，并重写以下方法：
        void detect(vehicles) 方法，传入车辆对象列表，检测数据并存储
        (该方法将会在车辆一次被检测时执行 start_detect_event(vehicle)
         在车辆最后一次被检测时执行 finish_detect_event(vehicle)
         如有需要请重写这两个事件)
        out_dict data_parocessing 方法，将检测器数据处理为以下格式：
        out_dict为返回字典： {'vehicles_data': dict1, 'road_data': dict2}
        vehicles_data 为车辆数据字典，例如：
        {vehicle : {
            enter_time :
            change_lane_times :
            average_speed :
            out_time :
            }

        }
        road_data 为道路数据字典，例如：
        {capacity: }
注： 一些数据可以通过给车辆对象添加字段来方便检测（如，换道次数）
'''

# 默认检测所有时间 所有空间
class Detector:
    def __init__(self, start_time=0, end_time=float('inf'),
                 start_x=0, end_x=float('inf'), is_circle_border=False):
        '''
        :param time_range: 检测器检测时间范围
        :param space_range: 检测器检测空间范围
        '''
        self.start_time = start_time  # 检测器开始检测时间
        self.end_time = end_time  # 检测器结束检测时间
        self.start_x = start_x  # 检测器开始检测位置
        self.end_x = end_x  # 检测器结束检测位置
        self.is_circle_border = is_circle_border # 是否为周期边界条件
        # 记录 detect_times 次 车辆速度和 最终求平均车速
        self.vehicles_data = {'v_sum': [], 'detect_times': [], 'change_lane_times': []}  # 车辆检测数据
        self.detecing_vehicles_df = pd.DataFrame(self.vehicles_data)  # 正在检测车辆数据表
        self.detecing_vehicles_df.index.name = '车辆index'
        self.completed_vehicles_df = pd.DataFrame(self.vehicles_data)  # 完成检测的车辆数据表
        self.completed_vehicles_df.index.name = '车辆index'
        self.flow = 0  # 检测路段末尾断面流量

    # 检测道路的平均车速和路段末尾断面流量
    def detect(self, cur_time, vehicles):
        for vehicle in vehicles:
            # 判断是否检测
            if self.need_detect(cur_time, vehicle):
                if vehicle.index not in self.detecing_vehicles_df.index:
                    # 车辆一次被检测时执行
                    self.start_detect_event(vehicle)
                # 检测车辆数据
                self.detect_vehicle(vehicle)
                # 当前车辆的数据字典（每次对满足条件的车辆进行）
            elif vehicle.index in self.detecing_vehicles_df.index:
                # 已在正在检测字典中，但不需要检测，即已完成检测
                self.finish_detect_event(vehicle)
                # 将检测数据归档到已检测车辆数据表中
                self.completed_vehicles_df = self.completed_vehicles_df.append(self.detecing_vehicles_df.loc[vehicle.index, :])
                self.detecing_vehicles_df.drop(labels=vehicle.index, inplace=True)

    # 数据处理方法 将检测器获得原始数据处理为特定格式
    def data_processing(self):
        out_dict = {}  # 数据处理返回结果字典
        # 计算各车平均车速
        self.completed_vehicles_df.loc[:, 'average_speed'] = (self.completed_vehicles_df.loc[:, 'v_sum'] /
                                                          self.completed_vehicles_df.loc[:, 'detect_times'])
        # 计算所有车辆平均车速的平均
        out_dict['average_speed'] = self.completed_vehicles_df.loc[:, 'average_speed'].mean()
        out_dict['flow'] = self.flow
        return out_dict


    '''
    如果要统计个性化数据  需要重写的方法（需要统计流量和平均车速需要执行超类方法）
    '''
    # 判断当前是否需要检测：是否到检测时间
    def need_detect(self, cur_time, vehicle):
        """
        :param cur_time:  当前时间
        :param vehicle:  待检测车辆
        :return: 是否需要检测
        """
        if type(vehicle) == Wall:
            return False
        if (self.start_time <= cur_time <= self.end_time
                and self.start_x <= vehicle.x <= self.end_x):
            return True
        else:
            return False

    # 车辆一次被检测时执行该事件
    def start_detect_event(self, vehicle):
        self.detecing_vehicles_df.loc[vehicle.index, 'v_sum'] = 0
        self.detecing_vehicles_df.loc[vehicle.index, 'detect_times'] = 0

    # 车辆最后一次被检测时执行该事件
    def finish_detect_event(self, vehicle):
        # 统计流量断面为检测路段某位断面
        self.flow += 1

    # 检测车辆数据（每次对满足条件的车辆进行）
    def detect_vehicle(self, vehicle):
        # 记录数据
        self.detecing_vehicles_df.loc[vehicle.index, 'v_sum'] += vehicle.v
        self.detecing_vehicles_df.loc[vehicle.index, 'detect_times'] += 1

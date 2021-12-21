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


class Detector:
    def __init__(self, time_range, space_range):
        '''
        :param time_range: 检测器检测时间范围
        :param space_range: 检测器检测空间范围
        '''
        self.start_time = time_range[0]  # 检测器开始检测时间
        self.end_time = time_range[1]  # 检测器结束检测时间
        self.start_x = space_range[0]  # 检测器开始检测位置
        self.end_x = space_range[1]  # 检测器结束检测位置
        self.detecing_vehicles = {}  # 正在检测车辆数据字典
        self.completed_vehicles = {}  # 完成检测的车辆数据字典
        self.flow = 0  # 检测路段末尾断面流量

    # 检测道路的平均车速和路段末尾断面流量
    def detect(self, cur_time, vehicles):
        for vehicle in vehicles:
            # 判断是否检测
            if self.need_detect(cur_time, vehicle):
                if vehicle not in vehicles:
                    # 车辆一次被检测时执行
                    self.start_detect_event(vehicle)
                # 当前车辆的数据字典
                cur_dict = self.detecing_vehicles[vehicle]
                # 记录 detect_times 次 车辆速度和 最终求平均车速
                cur_dict['v_sum'] = cur_dict.get('v_sum', 0) + vehicle.v
                cur_dict['detect_times'] = cur_dict.get('detect_times', 0) + 1
            elif vehicle in self.detecing_vehicles:
                self.finish_detect_event(vehicle)

    # 数据处理方法 将检测器获得原始数据处理为特定格式
    def data_processing(self, detect_dict, capacity, ):
        pass

    # 判断当前是否需要检测：是否到检测时间
    def need_detect(self, cur_time, vehicle):
        """
        :param cur_time:  当前时间
        :param vehicle:  待检测车辆
        :return: 是否需要检测
        """
        if (self.start_time <= cur_time <= self.end_time
                and self.start_x <= vehicle.x <= self.end_x):
            return True
        else:
            return False

    # 车辆一次被检测时执行该事件
    def start_detect_event(self, vehicle):
        pass

    # 车辆最后一次被检测时执行该事件
    def finish_detect_event(self, vehicle):
        # 已在正在检测字典中，但不需要检测，即已完成检测
        self.completed_vehicles[vehicle] = self.detecing_vehicles.pop(vehicle)
        # 统计流量断面为检测路段某位断面
        self.flow += 1

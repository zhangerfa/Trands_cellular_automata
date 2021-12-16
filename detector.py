# '''
# 只统计走完M1全段的车辆 的数据
# 平均换道率  ：  换道次数/(dt*车)
# 平均运行速度 ： m / (dt*车)
# M1段流量 ： M1结尾断面通过车辆数/dt
# 统计数据结构：换道次数，检测器记录每辆车进入和驶出M1段的时刻
#             M1段的累计换道次数，M1段的累计速度和
# {vehicle : {
#             enter_time :
#             change_lane_times :
#             v_sum :
#             out_time :
#             }
#
# }
# capacity
# '''
# import road
#
#
# class Detector():
#     def __init__(self, start_time):
#         self.start_time = start_time  # 检测器开始检测时间
#         self.detecing_vehicles = {} # 正在检测车辆数据字典
#         self.completed_vehicles = {} # 完成检测的车辆数据字典
#         self.capacity = 0 # 通行能力
#
#     # 判断当前是否需要检测：是否到检测时间
#     def need_detect(self, cur_time):
#         if cur_time >= self.start_time:
#             return True
#         else:
#             return False
#
#
# # 布设在M1上的检测器
# class M1_detector(Detector):
#
#     def __init__(self, road, start_time):
#         super().__init__(start_time)
#         self.road = road # 检测道路
#         # 获取M1位置范围
#         for x in road.lanes[0].section.keys():
#             type = road.lanes[0].section.get(x)
#             if type == LaneType.M0:
#                 self.start_x = x + 1
#             if type == LaneType.M1:
#                 self.end_x = x
#
#     # 判断输入车辆是否需要检测：是否在M1段
#     def vehicle_need_detect(self, vehicle):
#         if self.start_x <= vehicle.x <= self.end_x:
#             return True
#         else:
#             return False
#
#     # 检测M1段所有车辆信息
#     def detect(self , cur_time):
#         if self.need_detect(cur_time):
#             # 更新车速总和
#             for lane in self.road.lanes:
#                 vehicle_list = lane.vehicles
#                 for v in vehicle_list:
#                     # 判断是否需要检测
#                     if self.vehicle_need_detect(v):
#                         # 对已在M1段但未被检测过车辆初始化
#                         if v not in self.detecing_vehicles:
#                             self.detecing_vehicles[v] = {'enter_time': cur_time,
#                                                          'change_lane_times': 0,
#                                                          'v_sum': 0,
#                                                          'v_sum_times': 0
#                                                         }
#                         # v_sum 更新
#                         cur_v_sum = self.detecing_vehicles[v].get('v_sum')
#                         self.detecing_vehicles[v]['v_sum'] = cur_v_sum + v.v
#                         self.detecing_vehicles[v]['v_sum_times'] = \
#                             self.detecing_vehicles[v]['v_sum_times'] + 1
#                     elif v in self.detecing_vehicles:
#                         # 已在正在检测字典中，但不需要检测，即已完成检测
#                         self.completed_vehicles[v] = self.detecing_vehicles.pop(v)
#                         self.completed_vehicles[v]['out_time'] = cur_time - 1
#                         self.capacity += 1
#
#
#     # 数据处理方法 将检测器获得原始数据处理为特定格式
#     def data_processing(self, detect_dict, capacity, ):
#         '''
#         {vehicle : {
#                     enter_time :
#                     change_lane_times :
#                     v_sum :
#                     out_time :
#             }
#         }
#         '''
#         out_dict = {'capacity': capacity,
#                     'average_speed': 0,
#                     'change_lane_frequency': 0
#                     }
#         car_num = len(detect_dict)  # 总共完成检测的车辆数
#         # 计算每车各项平均数据之和
#         for value in detect_dict.values():
#             duration = value['out_time'] - value['enter_time']  # 该车通过M1段的运行时间（dt个数）
#             if duration == 0:
#                 # 一个无效数据
#                 car_num -= 1
#                 continue
#             v_sum = value['v_sum']
#             change_lane_times = value['change_lane_times']
#             cur_average_speed = out_dict.get('average_speed')
#             cur_change_lane_frequency = out_dict.get('change_lane_frequency')
#             # 平均运行车速 （元胞/dt）
#             out_dict['average_speed'] = v_sum / duration + cur_average_speed
#             # 换道率（次/dt）
#             out_dict['change_lane_frequency'] = change_lane_times / duration + \
#                                                 cur_change_lane_frequency
#         # 计算各项平均值
#         print(out_dict)
#         out_dict['average_speed'] = out_dict.get('average_speed') / car_num
#         out_dict['change_lane_frequency'] = out_dict.get('change_lane_frequency') / car_num
#         return out_dict
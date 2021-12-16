'''
py 3.8
pip install xlwt
'''

from road import *
import xlwt

'''
所有长度单位为元胞（3.75 * 3.75）
'''

# M1 长度从M1_range[0] 缩减到 M1_range[1] 进行仿真 返回检测器
def M1_reduce(M1_range , car_percent):
    M1_length_detector_dict = {}
    for M1_length in range(M1_range[0] , M1_range[1] - 1 , -2):
        # 打印进度
        print('car_percent:' + str(car_percent) + ',' + 'M1_length:' + str(M1_length) + ' 开始仿真')
        # M1 长度以2为步长缩减
        L1 = Lane({LaneType.M0: 300 , LaneType.M1: M1_length , LaneType.M2: 52} ,
                  {VehicleType.car: car_percent , VehicleType.truck: 1-car_percent})
        L2 = Lane({LaneType.M0: 300 , LaneType.M1: M1_length , LaneType.M2: 52} ,
                  {VehicleType.car: car_percent , VehicleType.truck: 1-car_percent})
        L3 = Lane({LaneType.M0: 300 , LaneType.M1: M1_length} ,
                  {VehicleType.car: car_percent , VehicleType.truck: 1-car_percent})
        # 创建道路
        lanes = [L1, L2, L3]
        road = Road(lanes)
        road.run(2000)
        # 检测器数据整理
        detect_dict = road.m1_decorator.completed_vehicles
        '''
        {vehicle : {
                    enter_time :
                    change_lane_times :
                    v_sum :
                    out_time :
            }
        }
        '''
        capacity = road.m1_decorator.capacity
        out_dict = {'capacity' : capacity ,
                    'average_speed' : 0 ,
                    'change_lane_frequency' : 0
                    }
        # 计算每车各项平均数据之和
        car_num = 0  # 总共完成检测的车辆数
        for value in detect_dict.values():
            car_num += 1
            duration = value['out_time'] - value['enter_time'] # 该车通过M1段的运行时间（dt个数）
            v_sum = value['v_sum']
            v_sum_times = value['v_sum_times']
            change_lane_times = value['change_lane_times']
            cur_average_speed = out_dict.get('average_speed')
            cur_change_lane_frequency = out_dict.get('change_lane_frequency')
            # 平均运行车速 （元胞/dt）
            out_dict['average_speed'] = v_sum / v_sum_times + cur_average_speed
            # 换道率（次/dt）
            out_dict['change_lane_frequency'] = change_lane_times / v_sum_times + \
                                                cur_change_lane_frequency
        # 计算各项平均值
        out_dict['average_speed'] = out_dict.get('average_speed') / car_num
        out_dict['change_lane_frequency'] = out_dict.get('change_lane_frequency') / car_num
        M1_length_detector_dict[M1_length] = out_dict
    return M1_length_detector_dict

# 小汽车占比从car_percent_list[0]缩减到car_percent_list[-1]
def car_percent_reduce(car_percent_list , M1_range):
    car_percent_detector_dic = {}
    for car_percent in car_percent_list:
        M1_length_detector_dict = M1_reduce(M1_range , car_percent)
        car_percent_detector_dic[car_percent] = M1_length_detector_dict
    return car_percent_detector_dic

############# 程序入口
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
for i in range(1):
    # 小汽车占比缩减列表
    #car_percent_list = [1 , 0.95 , 0.9 , 0.85]
    car_percent_list = [1]
    # 缩减区 长度以步长为2 缩减范围（从大到小）
    M1_range = [48 , 8]
    # 得到检测器数据
    car_percent_detector_dict = car_percent_reduce(car_percent_list , M1_range)
    '''
    {car_percent : {
                    M1_length : {
                                    capacity :
                                    average_speed :
                                    change_lane_frequency :
                                 }
                    ......
                    }
    ......
    }
    '''
    for car_percent in car_percent_list:
        for m1_length in range(M1_range[0] , M1_range[1] - 1 , -2):
            cur_dict = car_percent_detector_dict[car_percent][m1_length]
            sheet.write(row , 0 , car_percent)
            sheet.write(row, 1 , m1_length)
            sheet.write(row, 2, cur_dict['capacity'])
            sheet.write(row, 3, cur_dict['average_speed'])
            sheet.write(row, 4, cur_dict['change_lane_frequency'])
            row += 1
    # 保存在path 中
    workbook.save(path)
    print('数据已保存')
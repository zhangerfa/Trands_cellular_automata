'''
提供车道数据结构
车道由路段构成  并保存有车道上的所有车辆对象
'''

from enum import Enum
import random

# 车道类型枚举类
from math import exp


class LaneType(Enum):
    M0 = '战场路段'
    M1 = '缩减路段'
    M2 = '施工路段'

# 车辆类型枚举类 值为生成该类车辆的构造方法
class VehicleType(Enum):
    car = '小汽车'
    truck = '货车'

# vehicle_type_percent {type ： percent}
# section 路段构成（路段类型 ： 长度）
class Lane():
    def __init__(self , section , vehicle_type_percent_dict):
        self.lam = 0.4 # 泊松分布 λ 参数 dt时间内平均到达车辆数
        self.section = {} # 路段构成（该段末尾位置 ： 类型）
        self.length = 0 # 车道长度
        # 更新路段构成和车道长度
        for type in section:
            self.length += section[type]
            self.section[self.length] = type
        # 将传入各类车辆所占百分比转换为（0，1）之间的具体区段
        self.type_percent = {} # 如（0，0.1）生成car （0.1，1）生成truck
        sum = 0
        for type in vehicle_type_percent_dict:
            percent = vehicle_type_percent_dict[type]
            sum += percent
            self.type_percent[sum] = type
            # 当某种车百分百出现 其他车不会生成
            if percent == 1:
                break
        self.vehicles = [] # 车辆构成 以x的从小到大顺序 存储vehicle list

    # 以泊松分布车道到达
    def is_arrive(self):
        poisson = self.lam *  exp(self.lam) # dt足够小，只计算dt时间内来一辆车概率
        random_num = random.random()
        if random_num < poisson:
            return True
        else:
            return False

    def which_section(self , vehicle):
        if vehicle in self.vehicles:
            for x in self.section.keys():
                if x > vehicle.x:
                    return self.section[x]
        else:
            print('车辆不在当前车道')
            return

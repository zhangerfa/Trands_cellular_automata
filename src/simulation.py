from src.vehicle_enum import Direction

"""
封装仿真过程
@:param vehicle_generator 车辆生成器，用于生成车辆
（开口生成器就运行开口边界条件，等间距生成器就运行周期边界条件）
"""


class Simulation:
    def __init__(self, road, vehicle_generator, detector=None):
        self.road = road
        self.vehicles = []  # 道路上所有车辆对象列表
        self.vehicle_generator = vehicle_generator  # 车辆生成器
        self.detector = detector  # 检测器
        # 判断是周期边界条件还是开口边界条件
        self.is_circle_border = True if self.vehicle_generator.lam is None else False

    # 运行仿真，返回检测器数据处理结果
    def run(self, time_max):
        for time in range(time_max):
            # 道路状态更新
            self.run_one_time()
            # 检测器检测所有车辆
            self.detector.detect(time, self.vehicles)
        # 返回检测器数据处理结果
        return self.detector.data_processing()

    # 道路状态更新（仿真时间前进一步）
    def run_one_time(self):
        if not self.is_circle_border:
            # 开口新车辆到达
            self.__new_vehicle_arrive()
        # 车辆更新
        self.__update_vehicle()

    # 计算车辆密度 veh/km  如果未给出不同种类车辆对veh的换算系数，则单位为 辆/km
    def get_density(self):
        return (len(self.vehicles) / self.road.lane_num) / self.road.length * 1000

    # 检测当前规则是否会造成撞车
    def has_accident(self):
        pass

    def __update_vehicle(self):
        for v in self.vehicles:
            # 换道
            direction = v.change_lane()
            # 换道后更新周围车辆信息
            self.road.update_around(v, direction)
            # 更新速度
            v.update_v()
            # 更新位置
            v.x = (v.x + v.v * v.direction.value) % self.road.length
            # 车辆驶出判断
            if not self.__out_road(v):
                # 跟驰后更新周围车辆信息
                self.road.__update_lane(v)
            elif not self.is_circle_border:
                # 开口边界条件下，驶出道路的车辆从道路移出
                self.__remove_vehicle(v)

    # 判断车辆是否驶出道路，如果驶出就从道路移出
    def __out_road(self, v):
        """
        :param v: 车辆
        :return: 车辆驶出道路返回True 否则 False
        """
        if v.direction == Direction.right and v.x >= self.road.length or \
                v.direction == Direction.right and v.x <= 0:
            self.__remove_vehicle(v)
            return True
        else:
            return False

    # 道路开口有新车到达
    def __new_vehicle_arrive(self):
        for lane in range(self.road.lane_num):
            # 调用车辆生成器当前车道生成车辆
            new_vehicles = self.vehicle_generator.new_vehicle(lane, self)
            for new_vehicle in new_vehicles:
                if new_vehicle is not None:
                    self.__add_vehicle(new_vehicle)

    def __remove_vehicle(self, v):
        pass

    def __add_vehicle(self, new_vehicle):
        pass

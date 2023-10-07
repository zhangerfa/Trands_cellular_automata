import matplotlib.pyplot as plt


class Drawer:
    # 创建画布
    fig = plt.figure()
    ax = fig.add_subplot(111)

    def __init__(self, simulation):
        self.simulation = simulation

    # 运行动画展示
    def show(self, time_max, pause_time=0.3):
        # 运行仿真
        for time in range(time_max):
            # 道路状态更新
            self.simulation.run_one_time()
            # 图像更新
            plt.cla()
            self.__draw()
            # 暂停
            plt.pause(pause_time)

    # 画图函数: 画出道路和车辆
    # 元胞坐标为左下角点坐标
    def __draw(self):
        vehicles = self.simulation.vehicles
        road = self.simulation.road
        is_circle_border = self.simulation.is_circle_border
        # 网格线范围
        y_min = 0
        y_max = road.lane_num
        x_min = 0
        x_max = road.length
        # 纵线
        for x in range(x_max):
            plt.plot([x, x], [y_min, y_max], 'k', linewidth=0.5)
        # 横线
        for y in range(y_max):
            plt.plot([x_min, x_max], [y, y], 'k', linewidth=0.5)
        plt.plot([x_min, x_max], [y_max, y_max], 'k', linewidth=0.5)
        # 绘制车辆
        for v in vehicles:
            # 车辆左下角坐标
            vehicle_range = get_range(v, is_circle_border)
            for position in vehicle_range:
                x = position[1]
                y = position[0]
                # 画出一个矩形
                rect = plt.Rectangle((x, y), 1, 1, facecolor=v.color.value)
                self.ax.add_patch(rect)
        plt.xlim(0, x_max)
        plt.ylim(-1, y_max)
        # 绘制分界线
        for lane_index in range(x_max):
            lane = road.lanes[lane_index]
            for end_x in lane.end_x_section_dict:
                plt.plot([end_x, end_x], [lane_index, lane_index + 1], 'k')
        # x y 轴等比例
        self.ax.set_aspect('equal', adjustable='box')
        # 隐藏坐标轴
        plt.axis('off')


# 获取车辆所在元胞的坐标
def get_range(vehicle, is_circle_border):
    lane = vehicle.lane
    x = vehicle.x
    space_range = []  # 车辆所在所有元胞的坐标
    for delta_x in range(vehicle.length):
        for delta_lane in range(vehicle.width):
            cur_lane = lane - delta_lane
            cur_x = x - delta_x * vehicle.direction.value
            if is_circle_border:
                cur_x = cur_x % vehicle.lane.length
            space_range.append([cur_lane, cur_x])
    return space_range

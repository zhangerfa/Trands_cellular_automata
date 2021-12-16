# 换道函数
"""
车辆坐标是 车辆最前方（前进方向）元胞的 左下角
整个车辆所占矩形的左下角坐标为 (vehicle.lane, vehicle.x + 1 - vehicle.length)
"""

import matplotlib.pyplot as plt


# 运行动画展示
def show(road, time_max):
    # 创建画布
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # 运行仿真
    for time in range(time_max):
        # 道路状态更新
        road.update()
        # 图像更新
        plt.cla()
        draw(ax, road)
        plt.pause(0.1)
    # 删除画布
    plt.close(fig)


# 画图函数
def draw(ax, road):
    # 网格线范围
    y_min = 0
    y_max = road.lane_num + 1
    x_min = 0
    x_max = road.length + 1
    # 纵线
    for x in range(x_max):
        plt.plot([x, x], [y_min, y_max], 'k', linewidth=0.5)
    # 横线
    for y in range(y_max):
        plt.plot([x_min, x_max], [y, y], 'k', linewidth=0.5)
    plt.plot([x_min, x_max], [y_max, y_max], 'k', linewidth=0.5)
    # 绘制车辆
    for v in road.vehicles:
        # 车辆左下角坐标
        x = v.x + 1 - v.length
        y = v.lane
        # 画出一个矩形
        rect = plt.Rectangle((x, y), v.length, 1, facecolor=v.color.value)
        ax.add_patch(rect)
    plt.xlim(0, road.length)
    plt.ylim(-1, road.lane_num)
    # 绘制分界线
    for lane_index in range(road.lane_num):
        lane = road.lanes[lane_index]
        for end_x in lane.end_x_section_dict:
            plt.plot([end_x, end_x], [lane_index, lane_index + 1], 'k')
    # x y 轴等比例
    ax.set_aspect('equal', adjustable='box')
    # 隐藏坐标轴
    plt.axis('off')

    # # 绘制施工区
    # lane = road.lanes[road.shortest_lane]  # 施工路段
    # startx_x = lane.length
    # length = road.length - startx_x
    # rect = plt.Rectangle((startx_x, road.shortest_lane), length, 1, facecolor=[0, 1, 0])
    # ax.add_patch(rect)
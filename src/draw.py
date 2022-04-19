# 换道函数
"""
每个元胞的坐标左下角坐标
"""

import matplotlib.pyplot as plt


# 画图函数
def draw(ax, road):
    # 网格线范围
    y_min = 0
    y_max = road.space.lane_num
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
    for v in road.vehicles:
        # 车辆左下角坐标
        vehicle_range = v.get_space_range()
        for position in vehicle_range:
            x = position[1]
            y = position[0]
            # 画出一个矩形
            rect = plt.Rectangle((x, y), 1, 1, facecolor=v.color.value)
            ax.add_patch(rect)
    plt.xlim(0, road.length)
    plt.ylim(-1, road.space.lane_num)
    # 绘制分界线
    for lane_index in range(road.space.lane_num):
        lane = road.space.lanes[lane_index]
        for end_x in lane.end_x_section_dict:
            plt.plot([end_x, end_x], [lane_index, lane_index + 1], 'k')
    # x y 轴等比例
    ax.set_aspect('equal', adjustable='box')
    # 隐藏坐标轴
    plt.axis('off')

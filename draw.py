import matplotlib.pyplot as plt
import vehicles as vs

# 画图函数
def draw(ax , road):
    ### 绘制离散空间网格线
    # 纵线
    y_min = 0
    y_max = 2 + 1
    x_min = 0
    x_max = 400 + 1
    for x in range(x_max):
        plt.plot([x , x] , [y_min , y_max] , 'k' , linewidth=0.5)
    # 横线
    for y in range(y_max):
        plt.plot([x_min , x_max] , [y , y] , 'k' , linewidth=0.5)
    plt.plot([x_min, x_max], [y_max, y_max], 'k' , linewidth=0.5)
    # 绘制车辆
    for lane in road.lanes:
        vehicles = lane.vehicles
        for c in vehicles:
            # 向施工路段增加一辆永不移动的车辆以保持求车距函数的一致性
            if c.id == -1:
                continue
                # rect = plt.Rectangle((c.x - c.length, c.lane), c.length, 1, facecolor=[0,0,0])
                # ax.add_patch(rect)
            rect = plt.Rectangle((c.x - c.length, c.lane), c.length, 1, facecolor=c.color.value)
            ax.add_patch(rect)
    plt.xlim(0, 300)
    plt.ylim(-50, 50)
    # 绘制施工区
    lane = road.lanes[road.shortest_lane] # 施工路段
    startx_x = lane.length
    length = road.length - startx_x
    rect = plt.Rectangle((startx_x, road.shortest_lane), length , 1, facecolor=[0,1,0])
    ax.add_patch(rect)
    # 绘制分界线
    for x in lane.section.keys():
        plt.plot([x, x] , [-10, 10] , 'k')
    flag = True

# 运行效果展示函数
def show(road , timeMax):
    # 创建画布
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # 开始仿真
    for time in range(timeMax):
        road.new_vehicle_arrive()
        # 车辆换道
        road.change_lane()
        # 车辆位置更新
        road.update_x()
        # 图像更新
        plt.cla()
        draw(ax , road)
        plt.pause(0.1)
    # 删除画布
    plt.close(fig)
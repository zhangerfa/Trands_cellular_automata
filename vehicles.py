'''
车辆状态改变函数库
包括车间距获取函数 和 车辆位置更新函数
'''
import vehicle as v

### 车间距获取函数
# 获取前车距
def get_gap(vehicle):
    if vehicle.front is None:
        return float('inf')
    return vehicle.front.x - vehicle.x - vehicle.front.length


# 获取左前车距
def get_gap_left(vehicle):
    if vehicle.left_front is None:
        return float('inf')
    return vehicle.left_front.x - vehicle.x - vehicle.left_front.length


# 获取右前车距
def get_gap_right(vehicle):
    if vehicle.right_front is None:
        return float('inf')
    return vehicle.right_front.x - vehicle.x - vehicle.right_front.length


# 获取左后车距
def get_gaph_left(vehicle):
    if vehicle.left_back is None:
        return float('inf')
    return vehicle.left_back.x - vehicle.x - vehicle.left_back.length


# 获取右后车距
def get_gaph_right(vehicle):
    if vehicle.right_back is None:
        return float('inf')
    return vehicle.right_back.x - vehicle.x - vehicle.right_back.length


### 车辆位置更新函数
# 状态更新
def update_status(vehicle):
    # 向施工路段增加一辆永不移动的车辆以保持求车距函数的一致性
    if vehicle.id == -1:
        return
    gap = get_gap(vehicle)  # 前车距
    # 前车的间距大于等于高速行驶车辆的期望跟车间距 : 高速行驶
    if gap >= vehicle.gap_desire:
        vehicle.status = v.Status.fast
    elif gap >= vehicle.sp + 1:
        vehicle.status = v.Status.slow
    else:
        vehicle.status = v.Status.static


# 位置更新
def update_x(vehicle):
    update_status(vehicle)
    if vehicle.status == v.Status.fast:
        vehicle.v = vehicle.s_max
        vehicle.x += vehicle.s_max
    elif vehicle.status == v.Status.slow:
        # 平均速度行驶
        vehicle.x += vehicle.sp
        vehicle.v = vehicle.sp
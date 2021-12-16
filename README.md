# Trands_cellular_automata
 用于交通流微观仿真的元胞自动机建模工具
![image](https://github.com/zhangerfa/Trands_cellular_automata/blob/main/helper/%E5%85%83%E8%83%9E%E8%87%AA%E5%8A%A8%E6%9C%BA%E5%B1%95%E7%A4%BA.gif)

## 建模步骤
### 定义自己的车辆类
定义自己的车辆类，也可以是其他交通参与者，并让自己的车辆类继承`vehicle.Vehicle` 类
自己定义的车辆类需要实现`void update_v()`方法
如果换道规则中优先向右侧（相对于车辆前进方向）换道 需要实现以下两个方法：
`boolean can_change_lane(direction) ` 方法判断能否向传入方向换道 `direction`为 `Direction`对象
`boolean need_change_lane()`判断是否需要换道
如果有特殊换道顺序（如优先向非施工区换道）则需要重写`road.change_lane(road)`仍然建议实现上述两个方法，并基于这两个方法实现`road.change_lane(road)`,以提高可读性

    # 小汽车类
    class Car(Vehicle):
        length = 2  # 车辆长度
        color = Color.red  # 车辆颜色
        sp = 2  # dt时间内车辆平均行驶的距离
        s_max = 4  # 在dt时间内车辆的最大行驶距离 也就是v_max
        gap_desire = 12  # 期望前车距

        # 更新车速
        def __update_v(self):
            pass

        # 判断能否向传入方向换道
        def can_change_lane(self, direction):
            pass

        # 判断是否需要换道
        def need_change_lane(self)
            pass
    
    # 货车类
    class Truck(Vehicle):
        length = 4
        color = Color.blue
        sp = 2
        s_max = 3
        gap_desire = 9

        # 更新车速
        def __update_v(self):
            self.v = 10
            
                # 更新车速
        def __update_v(self):
            pass

        # 判断能否向传入方向换道
        def can_change_lane(self, direction):
            pass

        # 判断是否需要换道
        def need_change_lane(self)
            pass

### 构建测试场景
车道可以由若干段组成，定义自己的车道类型，并创建车道
    
    # 创建车道类型
    class LaneType(Enum):
        M0 = '正常路段'
        M1 = '变窄路段'
        M2 = '施工路段'
        
    # 创建车道对象
    L1 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50})
    L2 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50})
    L3 = Lane({LaneType.M0: 100, LaneType.M1: 50})
    
道路对象由若干车道组成

    lanes = [L1, L2, L3]
还需要定义一个车辆生成器为道路生成车辆，车道生成器可以自己定义 或直接使用vehicle_generator.Vehicle_generator，该生成器可以从车道左侧以输入到达率（服从泊松分布）按照输入车辆比例随机生成车辆
    
    # 创建车辆生成器
    lam = 0.4 # 到达率
    vehicle_generator = Vehicle_generator({Car: 0.9, Truck: 0.1}, lam)
创建道路，得到仿真对象
    
    # 创建道路
    road = Road(lanes, vehicle_generator)
    
### 运行仿真
定义仿真总时间步

    time_max = 100

仿真动画展示
    
    road.show(time_max)
    
获取仿真数据

    road.run(time_max)

run() 方法运行完毕之后就可以得到检测器对象所存储的运行时获取的数据

### 数据存储

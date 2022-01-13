# Trands_cellular_automata
本项目用于构建交通流微观仿真的元胞自动机模型

 **食用前请注意：**

本项目为自己OOP练习之作，受限于能力，必然存在错误与不足，不敢保证依次项目所构建模型能达到预计结果，另一方面在性能方面考虑很少，跑模型时用时可能较长。因此，如用作科研请自行检验模型是否可靠，如有错误或改进之处，欢迎issue
![image](https://github.com/zhangerfa/Trands_cellular_automata/blob/main/helper/%E5%85%83%E8%83%9E%E8%87%AA%E5%8A%A8%E6%9C%BA%E5%B1%95%E7%A4%BA.gif)

## 建模步骤
详细例子可以看`main.py`，以下抛开具体模型举例
### 定义自己的车辆类
定义自己的车辆类，也可以是其他交通参与者，并让自己的车辆类继承`vehicle.Vehicle` 类
自己定义的车辆类需要实现`void update_v()`方法，更新车辆字段`v`
如果换道规则中优先向右侧（相对于车辆前进方向）换道 需要实现以下两个方法：
`boolean can_change_lane(direction) ` 方法判断能否向传入方向换道 `direction`为 `Direction`对象
`boolean need_change_lane()`判断是否需要换道
如果有特殊换道顺序（如优先向非施工区换道）则需要重写`road.change_lane(road)`仍然建议实现上述两个方法，并基于这两个方法实现`road.change_lane(road)`,以提高可读性



    # 小汽车类
    class Car(Vehicle):
        a_max = 4  # 最大加速度
        color = Color.red  # 车辆颜色
        v_max = 7  # 最大速度
        length = 2  # 车辆长度

        # 更新车速
        def __update_v(self):
            self.v = 10

        # 判断能否向传入方向换道
        def can_change_lane(self, direction):
            pass

        # 将车辆换道至传入车道
        def update_lane(self, desire_lane):
            pass

    # 货车类
    '''
    货车类具有和小汽车一样的行为时，只需要修改其某些字段
    '''
    class Truck(Car):
        a_max = 2  # 最大加速度
        color = Color.blue  # 车辆颜色
        v_max = 5  # 最大速度
        length = 4

### 构建测试场景
车道可以由若干段组成，定义自己的车道类型（可以不构建枚举类直接用'str'代替）

    # 创建车道类型
    class LaneType(Enum):
        M0 = '正常路段'
        M1 = '变窄路段'
        M2 = '施工路段'

基于车道类型创建车道，构建车道需要传入该车道的车道组成（自左到右不同车道类型的长度），以`{laneType1: length1, ...}`形式输入
（当车道短于其他道路长度（最长车道长度）时，不足部分将补为墙体）
        
    # 创建车道对象
    L1 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50})
    L2 = Lane({LaneType.M0: 100, LaneType.M1: 50, LaneType.M2: 50})
    L3 = Lane({LaneType.M0: 100, LaneType.M1: 50})
    
创建车道对象列表

    lanes = [L1, L2, L3]
    
还需要定义一个车辆生成器为道路生成车辆，车道生成器可以自己定义 或直接使用`vehicle_generator.Vehicle_generator`，该生成器可以从车道左侧以输入到达率（服从泊松分布）按照输入车辆比例随机生成车辆，以`{Vehicle子类名: 占比, ...}`形式输入
    
    # 创建车辆生成器
    lam = 0.4 # 到达率
    vehicle_generator = Vehicle_generator({Car: 0.9, Truck: 0.1}, lam)

最后创建检测器以获取需要的仿真数据，检测器可以使用`Dector`,该检测器可以检测指定时间段，指定空间范围内的平均行程车速和检测路段末尾断面流量。或基于`Dector`创建自己的检测器。创建自己的检测器时需要重写以下两个方法：

`void start_detect_event(vehicle)`  该方法将会在车辆一次被检测时执行 
`void finish_detect_event(vehicle)` 在车辆最后一次被检测时执行 

其中，检测器中存储车辆数据的是两个Dataframe，`detecing_vehicles_df`存储正在检测（位于检测时间段和检测空间段内）车辆数据
`completed_vehicles_df`存储完成检测（不包括未参与检测车辆）的车辆数据

基于上述两个方法和两个Dataframe就可以获取大多数数据，如果需要获取车辆行进间数据，请重写`void detect(vehicles)` 方法（上述两个事件就在此方法中执行），传入车辆对象列表，检测数据并存储到上述两个Dataframe中

最终仿真数据输出形式除将上述两个Dataframe直接输出外，仍然建议重写 `data_parocessing `方法，将检测器数据处理为需要的格式.
注： 一些数据可以通过给车辆对象添加字段来方便检测（如，换道次数）

以下以创建可以检测换道次数的检测器为例

    # 创建检测器(基础检测器可以检测道路流量、平均车速)
    class MyDector(Detector):

        # 将新增检测数据添加到监测数据字典{数据名称: 默认值}
        def __init__(self, time_range, space_range):
            super().__init__(time_range, space_range)
            self.vehicles_data['change_lane_times'] = 0

        def start_detect_event(self, vehicle):
            super(MyDector, self).start_detect_event(vehicle)
            # 第一次检测到车辆时记录车辆换道次数
            self.detecing_vehicles_df.loc[vehicle.index, 'change_lane_times'] = vehicle.change_lane_times

        def finish_detect_event(self, vehicle):
            super(MyDector, self).finish_detect_event(vehicle)
            # 最后一次检测到车辆时计算在检测路段的换道次数
            start_times = self.detecing_vehicles_df.loc[vehicle.index, 'change_lane_times']
            self.detecing_vehicles_df.loc[vehicle.index, 'change_lane_times'] = vehicle.change_lane_times - start_times

        def data_processing(self):
            out_dict = super(MyDector, self).data_processing()
            # 计算平均换道次数
            out_dict['change_lane_times'] = self.completed_vehicles_df.loc[:, 'change_lane_times'].mean()
            return out_dict
创建检测器

    time_range = [100, time_max]
    space_range = [100, 150]
    detector = MyDector(time_range, space_range)

最终由车道列表和车辆生成器创建道路，得到仿真对象
    
    # 创建道路
    road = Road(lanes, vehicle_generator, detector)
    
### 运行仿真
定义仿真总时间步

    time_max = 100

仿真动画展示，动画展示可以直观观察车辆运行状态，既能帮助判断规则本身及编程实现是否有错，也能对在自身规则下运动的车辆所可能遇到的情况有一个认知
    
    road.show(time_max)
    
获取仿真数据

    road.run(time_max)

run() 方法运行完毕之后就可以得到检测器对象所存储的运行时获取的数据

### 数据存储

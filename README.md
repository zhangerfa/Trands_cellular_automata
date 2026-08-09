

# TCA — Traffic Cellular Automata

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org)
[![Tests](https://img.shields.io/badge/tests-80%20passed-green)]()

交通流微观仿真元胞自动机框架。面向科研人员，提供灵活的脚手架——继承 `Vehicle`、重写跟车/换道规则即可构建自定义仿真模型。

## 特性

- **可编程脚手架** — 继承 `Vehicle` 基类，重写 `update_v` / `need_change_lane` / `can_change_lane` 即可定义任意跟车换道规则
- **NumPy 网格引擎** — 底层空间管理基于 NumPy 二维数组，邻居查找使用 `np.nonzero` 向量化操作
- **开口 / 周期边界** — 策略模式切换，无需修改仿真逻辑
- **CLI + 配置文件** — 内置车辆类型可直接通过 `tca run config.yaml` 运行，无需写代码
- **可视化** — matplotlib 动画 + 时空图导出（GIF / MP4 / PNG）
- **可扩展检测器** — 通过钩子方法自定义数据采集逻辑

## 安装

```bash
git clone https://github.com/zhangerfa/Trands_cellular_automata.git
cd Trands_cellular_automata
pip install -e ".[dev]"
```

## 快速开始

### 3 步跑通 NaSch 模型

```python
import random
from tca import Vehicle, Lane, Road, Simulation, Detector, CircularBoundary, UniformGenerator

# 1. 定义车辆规则
class NaSchCar(Vehicle):
    length = 1
    v_max = 5
    color = "blue"

    def update_v(self, ctx):
        gap = min(ctx.gap_front, self.v_max + 1)
        self.v = min(self.v + 1, self.v_max, int(gap))
        if random.random() < 0.3 and self.v > 0:
            self.v -= 1

# 2. 构建场景
road = Road(
    lanes=[Lane({"road": 200})],
    generator=UniformGenerator({NaSchCar: 1.0}, vehicle_num=40),
    boundary=CircularBoundary(),
)

# 3. 运行仿真
sim = Simulation(road, detector=Detector(start_time=100))
sim.run(steps=5000)
print(sim.detector.summary())
# => {'average_speed': 2.21, 'flow': 0}
```

### 多车道施工区仿真

```python
import random
from tca import Vehicle, Lane, Road, Simulation, Detector, OpenBoundary, PoissonGenerator, Direction

class Car(Vehicle):
    length = 2
    v_max = 7
    color = "blue"

    def update_v(self, ctx):
        gap = min(ctx.gap_front, self.v_max + 1)
        self.v = min(self.v + 1, self.v_max, int(gap))
        if random.random() < 0.2 and self.v > 0:
            self.v -= 1

    def need_change_lane(self, ctx):
        return ctx.gap_front < self.v_max

    def can_change_lane(self, ctx, direction):
        if direction == Direction.RIGHT:
            return ctx.gap_right_front > ctx.gap_front and ctx.gap_right_back > self.v_max
        else:
            return ctx.gap_left_front > ctx.gap_front and ctx.gap_left_back > self.v_max

class Truck(Car):
    length = 4
    v_max = 5
    color = "red"

lanes = [
    Lane({"普通车道": 100, "变窄路段": 50, "施工路段": 50}),
    Lane({"普通车道": 100, "变窄路段": 50, "施工路段": 50}),
    Lane({"普通车道": 100, "变窄路段": 50}),  # 短于其他车道，末端自动填充墙体
]

road = Road(lanes, PoissonGenerator({Car: 0.8, Truck: 0.2}, lam=0.4), OpenBoundary())
sim = Simulation(road, Detector(start_time=200, start_x=50, end_x=180))
sim.run(steps=10000)
print(sim.detector.summary())
# => {'average_speed': 6.39, 'flow': 6174}
```

## 核心概念

### 建模流程

```
定义车辆规则 → 构建车道 → 选择边界条件 → 配置生成器 → 创建道路 → 运行仿真 → 分析数据
```

### 自定义车辆规则

继承 `Vehicle`，重写以下方法：

| 方法 | 作用 | 必须重写 |
|------|------|----------|
| `update_v(ctx)` | 跟车规则：根据环境信息更新速度 `self.v` | 是 |
| `need_change_lane(ctx)` | 判断是否需要换道 | 换道时需要 |
| `can_change_lane(ctx, direction)` | 判断能否向指定方向换道 | 换道时需要 |

车辆类属性：

| 属性 | 含义 | 默认值 |
|------|------|--------|
| `length` | 车辆长度（元胞数） | 1 |
| `width` | 车辆宽度（车道数） | 1 |
| `color` | 可视化颜色 | `"blue"` |

### VehicleContext — 环境感知

规则方法的 `ctx` 参数提供当前车辆的周围环境信息，所有属性惰性计算（按需查询，不用不算）：

| 属性 | 含义 |
|------|------|
| `ctx.gap_front` | 前车距（元胞数） |
| `ctx.gap_back` | 后车距 |
| `ctx.gap_left_front` | 左前车距 |
| `ctx.gap_left_back` | 左后车距 |
| `ctx.gap_right_front` | 右前车距 |
| `ctx.gap_right_back` | 右后车距 |
| `ctx.front` | 前车 `Vehicle` 对象（无前车时为 `None`） |
| `ctx.back` | 后车 `Vehicle` 对象（无后车时为 `None`） |

无邻居时返回 `float('inf')`。注意：使用 `int()` 转换前需先截断无穷值，如 `min(ctx.gap_front, self.v_max + 1)`。

### 边界条件

| 类型 | 类名 | 行为 |
|------|------|------|
| 开口边界 | `OpenBoundary` | 车辆驶出道路即移除，需配合 `PoissonGenerator` 在入口生成新车 |
| 周期边界 | `CircularBoundary` | 位置取模回绕，车辆总数固定，配合 `UniformGenerator` 初始铺放 |

### 车辆生成器

| 类名 | 适用场景 | 参数 |
|------|----------|------|
| `PoissonGenerator` | 开口边界 | `vehicle_ratios`（车型比例）、`lam`（到达率）、`is_two_way`（双向） |
| `UniformGenerator` | 周期边界 | `vehicle_ratios`（车型比例）、`vehicle_num`（总车辆数） |

### 自定义检测器

继承 `Detector`，重写钩子方法采集自定义数据：

```python
from tca import Detector

class LaneChangeDetector(Detector):
    def _on_enter(self, vehicle):
        super()._on_enter(vehicle)
        self._active[vehicle.id]["initial_lane"] = vehicle.lane

    def _on_exit(self, vehicle):
        record = self._active[vehicle.id]
        record["lane_changes"] = abs(vehicle.lane - record["initial_lane"])
        super()._on_exit(vehicle)
```

钩子方法：

| 方法 | 触发时机 |
|------|----------|
| `_on_enter(vehicle)` | 车辆首次进入检测区域 |
| `_on_exit(vehicle)` | 车辆离开检测区域 |
| `_record(vehicle)` | 每步对检测区域内的车辆调用 |
| `_should_detect(time, vehicle)` | 判断是否需要检测 |

### 仿真控制

`Simulation.step()` 暴露单步接口，可以在循环中插入自定义逻辑：

```python
sim = Simulation(road, detector)
for i in range(10000):
    if i == 5000:
        road.grid.place_walls(lane=2, start_x=50, end_x=100)  # 第 5000 步封闭一段车道
    sim.step()
```

### 可视化

```python
from tca import Plotter

plotter = Plotter(road, figsize=(14, 3))

# 动画展示
anim = plotter.animate(sim, steps=500, interval=50)
plt.show()

# 保存 GIF
plotter.save("output.gif", sim, steps=500, fps=20)

# 时空图（科研论文常用）
fig = plotter.plot_spacetime(sim, steps=1000, lane=0)
fig.savefig("spacetime.png", dpi=150, bbox_inches="tight")
```

## CLI 用法

对于内置车辆类型（Auto、Car），可以直接通过命令行 + YAML 配置运行，无需写 Python 代码：

```bash
# 运行仿真并输出结果
tca run examples/config.yaml --steps 10000

# 导出数据到 CSV
tca run examples/config.yaml --steps 10000 --output results.csv

# 动画展示
tca show examples/config.yaml --steps 500

# 保存动画为 GIF
tca show examples/config.yaml --steps 500 --save animation.gif
```

YAML 配置文件格式：

```yaml
road:
  lanes:
    - sections: {"普通车道": 100}
    - sections: {"普通车道": 100}
  boundary: open  # open | circular

generator:
  type: poisson   # poisson | uniform
  lam: 0.4
  vehicles:
    Car: 0.9
    Auto: 0.1

detector:
  start_time: 10
  start_x: 20
  end_x: 80
```

## 项目结构

```
tca/
├── core/
│   ├── grid.py          # NumPy 二维网格，车辆放置/移除/邻居查找
│   ├── simulation.py    # 仿真引擎：step() 调度生成→换道→加速→移动→检测
│   └── boundary.py      # 边界条件策略：OpenBoundary / CircularBoundary
├── models/
│   ├── vehicle.py       # Vehicle 基类 + VehicleContext（惰性邻居查询）
│   ├── road.py          # Road：持有 Grid + 车辆列表，执行单步操作
│   ├── lane.py          # Lane：车道分段数据
│   └── enums.py         # Direction (LEFT/RIGHT), Color
├── rules/
│   └── builtin.py       # 内置 NaSch 车辆类型（Auto, Car），供 CLI 使用
├── detector/
│   └── detector.py      # Detector：dict 运行时记录 + pandas 输出
├── generator/
│   └── generator.py     # PoissonGenerator / UniformGenerator
├── viz/
│   └── plot.py          # Plotter：matplotlib 动画 + 时空图
└── cli.py               # CLI 入口：tca run / tca show

tests/                   # 80 个单元测试
examples/
├── basic_nasch.py       # NaSch 单车道周期边界示例
├── work_zone.py         # 多车道施工区开口边界示例
└── config.yaml          # CLI 配置文件示例
```

## 运行测试

```bash
pytest tests/ -v
```

## 依赖

| 包 | 用途 |
|----|------|
| numpy >= 1.24 | 网格空间管理 |
| matplotlib >= 3.7 | 可视化 |
| pandas >= 2.0 | 数据输出 |
| pyyaml >= 6.0 | CLI 配置解析 |
| click >= 8.0 | CLI 框架 |
| pytest >= 7.0 | 测试（开发依赖） |

## License

MIT

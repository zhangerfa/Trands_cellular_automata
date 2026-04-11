# TCA — Traffic Cellular Automata

交通流微观仿真元胞自动机框架。科研人员通过继承 `Vehicle` 类、重写跟车/换道规则即可构建自定义仿真模型。

## 安装

```bash
pip install -e ".[dev]"
```

## 快速开始

```python
import random
from tca import (
    Vehicle, Lane, Road, Simulation, Detector,
    CircularBoundary, UniformGenerator, Direction,
)

class NaSchCar(Vehicle):
    length = 1
    v_max = 5
    color = "blue"

    def update_v(self, ctx):
        gap = min(ctx.gap_front, self.v_max + 1)
        self.v = min(self.v + 1, self.v_max, int(gap))
        if random.random() < 0.3 and self.v > 0:
            self.v -= 1

lanes = [Lane({"road": 200})]
generator = UniformGenerator({NaSchCar: 1.0}, vehicle_num=40)
detector = Detector(start_time=100)
road = Road(lanes, generator, CircularBoundary())

sim = Simulation(road, detector)
sim.run(steps=5000)
print(detector.summary())
```

## 自定义车辆规则

继承 `Vehicle`，重写以下方法：

- `update_v(ctx)` — 跟车规则，通过 `ctx.gap_front` 等获取邻居信息
- `need_change_lane(ctx)` — 是否需要换道
- `can_change_lane(ctx, direction)` — 能否向指定方向换道

`ctx`（`VehicleContext`）提供的属性：

| 属性 | 含义 |
|------|------|
| `ctx.gap_front` | 前车距 |
| `ctx.gap_back` | 后车距 |
| `ctx.gap_left_front` | 左前车距 |
| `ctx.gap_left_back` | 左后车距 |
| `ctx.gap_right_front` | 右前车距 |
| `ctx.gap_right_back` | 右后车距 |
| `ctx.front` | 前车对象（或 None） |

## 自定义检测器

继承 `Detector`，重写钩子方法：

```python
class LaneChangeDetector(Detector):
    def _on_enter(self, vehicle):
        super()._on_enter(vehicle)
        self._active[vehicle.id]["initial_lane"] = vehicle.lane

    def _on_exit(self, vehicle):
        record = self._active[vehicle.id]
        record["lane_changes"] = abs(vehicle.lane - record["initial_lane"])
        super()._on_exit(vehicle)
```

## CLI 用法

```bash
# 运行仿真
tca run examples/config.yaml --steps 10000

# 运行并导出数据
tca run examples/config.yaml --steps 10000 --output results.csv

# 动画展示
tca show examples/config.yaml --steps 500

# 保存动画
tca show examples/config.yaml --steps 500 --save animation.gif
```

CLI 支持 `rules/builtin.py` 中的内置车辆类型（Auto, Car）。自定义规则请通过 Python 脚本使用。

## 项目结构

```
tca/
├── core/           # 仿真引擎：Grid, Simulation, Boundary
├── models/         # 领域模型：Vehicle, Road, Lane, Enums
├── rules/          # 内置规则：NaSch 车辆类型
├── detector/       # 检测器
├── generator/      # 车辆生成器
├── viz/            # 可视化
└── cli.py          # 命令行入口
```

## 运行测试

```bash
pytest tests/ -v
```

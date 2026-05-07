# 4-Colour-Map-Shadering

中国省级行政区四色问题求解与可视化

## 项目简介

四色定理指出：任何地图都可以用不超过四种颜色着色，使得相邻区域颜色不同。本项目实现中国 34 个省级行政区的四色问题求解，并通过交互式窗口展示求解过程。

## 项目结构

```
4-Colour-Map-Shadering/
├── four_color_solver.py          # 四色问题求解器（含启发式优化）
├── visualize_interactive.py      # 交互式可视化窗口
├── visualize_animation.py        # 入口脚本
├── visualize_map.py            # 静态地图可视化
├── china_provinces.json         # 地图数据缓存
└── output/                       # 输出文件夹
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `four_color_solver.py` | 核心求解器，包含邻接关系建模、MRV/度启发式/LCV/CBJ 优化、步骤历史记录 |
| `visualize_interactive.py` | 交互式可视化窗口，支持播放/暂停/步进/滑轨跳转 |
| `visualize_animation.py` | 入口脚本 |
| `visualize_map.py` | 生成静态地图图片 |

## 运行方式

### 交互式可视化（推荐）

```bash
python visualize_animation.py
```

功能：
- 点击「播放」按钮自动播放求解过程
- 拖动底部滑轨跳转到任意步骤
- 「上一步」「下一步」逐帧控制
- 「重置」回到起始状态
- 右下角滑块调节播放速度

### 静态地图

```bash
python visualize_map.py
```

生成静态着色地图图片，保存至 `output/` 文件夹。

## 算法说明

### 基础回溯算法

使用回溯算法（Backtracking）求解四色问题：

1. 每次为未着色的省份尝试四种颜色
2. 检查该颜色是否与已着色相邻省份冲突
3. 如冲突则尝试下一种颜色
4. 如四种颜色均失败则回溯到上一步

### 启发式优化

代码实现了多种启发式优化，显著提升求解效率：

| 启发式 | 说明 |
|--------|------|
| **MRV（最少剩余值）** | 优先选择“可选颜色最少”的未着色省份，尽早暴露冲突 |
| **Degree（度数启发式）** | MRV 打平时，选“未着色邻居最多”的省份，约束力最强 |
| **LCV（最少约束值）** | 优先尝试对邻居未来可选颜色影响最小的颜色 |
| **CBJ（冲突导向后向跳转）** | 回溯时优先跳转到导致冲突的变量 |

算法会记录每一步操作（着色/回溯），用于可视化展示。

### 与普通回溯对比

| 指标 | 基础回溯 | 优化后 |
|------|----------|--------|
| 选择策略 | 固定顺序 | MRV + Degree |
| 颜色顺序 | 固定 | LCV 动态排序 |
| 剪枝策略 | 仅 is_safe | + CBJ 冲突导向 |
| 回溯效率 | 较低 | 明显提升 |

## 依赖

```
geopandas
matplotlib
numpy
```

安装依赖：
```bash
pip install geopandas matplotlib numpy
```

## 模块化设计

求解器与可视化分离，便于复用：

```python
from four_color_solver import solve_four_color_with_history, PROVINCES, ADJACENCY, COLORS
from visualize_interactive import InteractiveVisualizer

result, steps = solve_four_color_with_history(PROVINCES, ADJACENCY, COLORS)

viz = InteractiveVisualizer(
    steps=steps,
    result=result,
    provinces=PROVINCES,
    adjacency=ADJACENCY,
    colors=COLORS,
    color_hex={"红": "#E74C3C", "绿": "#27AE60", "蓝": "#3498DB", "黄": "#F1C40F"},
    color_gray="#D3D3D3"
)
viz.show()
```
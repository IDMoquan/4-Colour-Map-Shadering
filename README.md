# 4-Colour-Map-Shadering

中国省级行政区四色问题求解与可视化

## 项目简介

四色定理指出：任何地图都可以用不超过四种颜色着色，使得相邻区域颜色不同。本项目实现中国 34 个省级行政区的四色问题求解，并通过交互式窗口展示求解过程。

## 项目结构

```
4-Colour-Map-Shadering/
├── four_color_solver.py          # 四色问题求解器
├── visualize_interactive.py      # 交互式可视化窗口
├── visualize_animation.py        # 入口脚本
├── visualize_map.py            # 静态地图可视化
├── china_provinces.json         # 地图数据缓存
└── output/                       # 输出文件夹
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `four_color_solver.py` | 核心求解器，包含邻接关系建模、回溯算法、步骤历史记录 |
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

使用回溯算法（Backtracking）求解四色问题：

1. 每次为未着色的省份尝试四种颜色
2. 检查该颜色是否与已着色相邻省份冲突
3. 如冲突则尝试下一种颜色
4. 如四种颜色均失败则回溯到上一步

算法会记录每一步操作（着色/回溯），用于可视化展示。

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
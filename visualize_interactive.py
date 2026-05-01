import urllib.request
import json
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider, Button
from four_color_solver import (
    PROVINCES, ADJACENCY, COLORS, COLOR_HEX, COLOR_GRAY,
    solve_four_color_with_history
)

CHINA_PROVINCES_GEOJSON_URL = "https://raw.githubusercontent.com/Ox0400/china-geojson/master/json/geo/china/china-province.geojson"

PROVINCE_NAME_MAPPING = {
    "北京市": "北京", "天津市": "天津", "河北省": "河北", "山西省": "山西", "内蒙古自治区": "内蒙古",
    "辽宁省": "辽宁", "吉林省": "吉林", "黑龙江省": "黑龙江", "上海市": "上海", "江苏省": "江苏",
    "浙江省": "浙江", "安徽省": "安徽", "福建省": "福建", "江西省": "江西", "山东省": "山东",
    "河南省": "河南", "湖北省": "湖北", "湖南省": "湖南", "广东省": "广东", "广西壮族自治区": "广西",
    "海南省": "海南", "重庆市": "重庆", "四川省": "四川", "贵州省": "贵州", "云南省": "云南",
    "西藏自治区": "西藏", "陕西省": "陕西", "甘肃省": "甘肃", "青海省": "青海", "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆", "香港特别行政区": "香港", "澳门特别行政区": "澳门", "台湾省": "台湾"
}

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def download_china_map():
    cache_path = os.path.join(os.path.dirname(__file__), "china_provinces.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    with urllib.request.urlopen(CHINA_PROVINCES_GEOJSON_URL, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return data

def standardize_name(name):
    return PROVINCE_NAME_MAPPING.get(name, name)

class InteractiveVisualizer:
    def __init__(self, steps, result, provinces, adjacency, colors,
                 color_hex, color_gray, gdf=None):
        self.steps = steps
        self.result = result
        self.provinces = provinces
        self.adjacency = adjacency
        self.colors = colors
        self.color_hex = color_hex
        self.color_gray = color_gray

        if gdf is None:
            geojson_data = download_china_map()
            self.gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
            self.gdf['标准名称'] = self.gdf['NAME'].apply(standardize_name)
            self.gdf = self.gdf.set_index('标准名称')
        else:
            self.gdf = gdf

        self.current_step = 0
        self.total_steps = len(self.steps)
        self.is_playing = False
        self.play_interval = 200

        self._setup_window()

    def _setup_window(self):
        self.fig = plt.figure(figsize=(20, 15))
        self.fig.patch.set_facecolor('#F8F9FA')

        ax_map = self.fig.add_axes([0.05, 0.12, 0.65, 0.82])
        ax_map.set_facecolor('#E8F4F8')
        ax_map.set_xlim(73, 136)
        ax_map.set_ylim(15, 55)
        ax_map.set_title('中国省级行政区四色问题求解过程', fontsize=18, weight='bold',
                        pad=15, color='#2C3E50')
        ax_map.set_xlabel('经度', fontsize=12)
        ax_map.set_ylabel('纬度', fontsize=12)
        ax_map.spines['top'].set_visible(False)
        ax_map.spines['right'].set_visible(False)
        self.ax_map = ax_map

        ax_slider = self.fig.add_axes([0.05, 0.04, 0.60, 0.04])
        self.slider = Slider(
            ax=ax_slider,
            label='步骤',
            valmin=0,
            valmax=self.total_steps - 1,
            valinit=0,
            valfmt='%d'
        )
        self.slider.valtext.set_text(f"0 / {self.total_steps - 1}")
        self.slider.on_changed(self._on_slider_change)

        btn_width = 0.065
        btn_height = 0.045

        ax_btn_prev = self.fig.add_axes([0.72, 0.42, btn_width, btn_height])
        self.btn_prev = Button(ax_btn_prev, '上一步')
        self.btn_prev.on_clicked(self._on_prev)

        ax_btn_next = self.fig.add_axes([0.72, 0.36, btn_width, btn_height])
        self.btn_next = Button(ax_btn_next, '下一步')
        self.btn_next.on_clicked(self._on_next)

        ax_btn_play = self.fig.add_axes([0.72, 0.30, btn_width, btn_height])
        self.btn_play = Button(ax_btn_play, '播放')
        self.btn_play.on_clicked(self._on_play)

        ax_btn_pause = self.fig.add_axes([0.72, 0.24, btn_width, btn_height])
        self.btn_pause = Button(ax_btn_pause, '暂停')
        self.btn_pause.on_clicked(self._on_pause)

        ax_btn_reset = self.fig.add_axes([0.72, 0.18, btn_width, btn_height])
        self.btn_reset = Button(ax_btn_reset, '重置')
        self.btn_reset.on_clicked(self._on_reset)

        ax_speed_label = self.fig.add_axes([0.72, 0.10, btn_width, 0.05])
        ax_speed_label.set_facecolor('#F8F9FA')
        ax_speed_label.axis('off')
        ax_speed_label.text(0.5, 0.5, '播放速度', ha='center', va='center', fontsize=10)

        self.speed_ax = self.fig.add_axes([0.80, 0.06, 0.12, 0.04])
        self.speed_slider = Slider(
            ax=self.speed_ax,
            label='',
            valmin=50,
            valmax=1000,
            valinit=self.play_interval,
            valfmt='%dms'
        )
        self.speed_slider.on_changed(self._on_speed_change)

        legend_patches = [mpatches.Patch(color=c, label=n)
                         for n, c in self.color_hex.items()]
        legend_patches.append(mpatches.Patch(color=self.color_gray, label='待着色'))
        self.ax_map.legend(handles=legend_patches, loc='lower right', fontsize=10,
                         title='四色方案', title_fontsize=12, framealpha=0.9)

        self.status_text = self.ax_map.text(0.02, 0.98, '', transform=self.ax_map.transAxes,
                                           verticalalignment='top', fontsize=11,
                                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        self._draw_step(0)
        self.fig.text(0.83, 0.10, '播放速度:', fontsize=9, ha='left')

    def _draw_step(self, step_idx):
        self.ax_map.clear()
        self.ax_map.set_facecolor('#E8F4F8')
        self.ax_map.set_xlim(73, 136)
        self.ax_map.set_ylim(15, 55)
        self.ax_map.set_title('中国省级行政区四色问题求解过程', fontsize=18, weight='bold',
                             pad=15, color='#2C3E50')
        self.ax_map.set_xlabel('经度', fontsize=12)
        self.ax_map.set_ylabel('纬度', fontsize=12)
        self.ax_map.spines['top'].set_visible(False)
        self.ax_map.spines['right'].set_visible(False)

        step = self.steps[step_idx]
        current_assignment = step['assignment']

        for i in range(len(self.gdf)):
            row = self.gdf.iloc[i]
            province = row.name

            if province not in self.provinces:
                continue

            if province in current_assignment:
                color = self.color_hex.get(current_assignment[province], self.color_gray)
            else:
                color = self.color_gray

            edge_color = '#2C3E50'
            linewidth = 0.8

            if step['action'] == 'backtrack' and province == step['province']:
                edge_color = '#E74C3C'
                linewidth = 2.5
            elif step['action'] == 'assign' and province == step['province']:
                edge_color = '#27AE60'
                linewidth = 2.5

            self.gdf.iloc[[i]].plot(ax=self.ax_map, color=color,
                                   edgecolor=edge_color, linewidth=linewidth)

            centroid = row.geometry.centroid
            short_name = province[:2]
            self.ax_map.annotate(short_name, xy=(centroid.x, centroid.y),
                                ha='center', va='center', fontsize=7,
                                color='#2C3E50', weight='bold')

        legend_patches = [mpatches.Patch(color=c, label=n)
                         for n, c in self.color_hex.items()]
        legend_patches.append(mpatches.Patch(color=self.color_gray, label='待着色'))
        self.ax_map.legend(handles=legend_patches, loc='lower right', fontsize=10,
                         title='四色方案', title_fontsize=12, framealpha=0.9)

        colored_count = len(current_assignment)
        self.status_text.set_text(f"步骤 {step_idx + 1}/{self.total_steps}\n"
                                  f"已着色: {colored_count}/{len(self.provinces)}\n"
                                  f"{step['message']}")

        self.fig.canvas.draw_idle()

    def _on_slider_change(self, val):
        self.current_step = int(val)
        self._draw_step(self.current_step)
        self.slider.valtext.set_text(f"{self.current_step} / {self.total_steps - 1}")

    def _on_prev(self, event):
        self.is_playing = False
        if self.current_step > 0:
            self.current_step -= 1
            self.slider.set_val(self.current_step)

    def _on_next(self, event):
        self.is_playing = False
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.slider.set_val(self.current_step)

    def _advance_step(self):
        if self.is_playing and self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.slider.set_val(self.current_step)
        elif self.current_step >= self.total_steps - 1:
            self.is_playing = False

    def _on_play(self, event):
        if self.current_step >= self.total_steps - 1:
            self.current_step = 0
            self.slider.set_val(0)
        self.is_playing = True
        self._start_timer()

    def _start_timer(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.timer = self.fig.canvas.new_timer(interval=self.play_interval)
        self.timer.add_callback(self._advance_step)
        if self.is_playing:
            self.timer.start()

    def _on_pause(self, event):
        self.is_playing = False
        if hasattr(self, 'timer'):
            self.timer.stop()

    def _on_reset(self, event):
        self.is_playing = False
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.current_step = 0
        self.slider.set_val(0)

    def _on_speed_change(self, val):
        self.play_interval = int(val)
        if self.is_playing:
            self._start_timer()

    def show(self):
        plt.show()

def main():
    print("正在求解四色问题...")
    result, steps = solve_four_color_with_history(PROVINCES, ADJACENCY, COLORS)
    print(f"求解完成，共 {len(steps)} 步计算")

    viz = InteractiveVisualizer(
        steps=steps,
        result=result,
        provinces=PROVINCES,
        adjacency=ADJACENCY,
        colors=COLORS,
        color_hex=COLOR_HEX,
        color_gray=COLOR_GRAY
    )

    print("点击「播放」按钮开始自动播放...")
    print("播放速度: 可通过右下角滑块调节（默认200ms/步）")

    viz.show()

if __name__ == "__main__":
    main()
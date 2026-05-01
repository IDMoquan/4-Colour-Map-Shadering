import urllib.request
import json
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import numpy as np
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

    print("下载中国省份地图数据...")
    with urllib.request.urlopen(CHINA_PROVINCES_GEOJSON_URL, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print("地图数据下载完成并已缓存")
    return data

def standardize_name(name):
    return PROVINCE_NAME_MAPPING.get(name, name)

def create_step_visualization():
    geojson_data = download_china_map()
    if not geojson_data:
        print("无法获取地图数据")
        return

    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    gdf['标准名称'] = gdf['NAME'].apply(standardize_name)
    gdf = gdf.set_index('标准名称')

    result, steps = solve_four_color_with_history(PROVINCES, ADJACENCY, COLORS)
    if not result:
        print("无法求解四色问题")
        return

    print(f"开始生成动画，共 {len(steps)} 步...")

    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#E8F4F8')

    ax.set_xlim(73, 136)
    ax.set_ylim(15, 55)
    ax.set_title('中国省级行政区四色问题求解过程', fontsize=18, weight='bold',
                pad=20, color='#2C3E50')
    ax.set_xlabel('经度', fontsize=12)
    ax.set_ylabel('纬度', fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    legend_patches = [mpatches.Patch(color=color, label=name)
                     for name, color in COLOR_HEX.items()]
    legend_patches.append(mpatches.Patch(color=COLOR_GRAY, label='待着色'))
    ax.legend(handles=legend_patches, loc='lower right', fontsize=10,
             title='四色方案', title_fontsize=12, framealpha=0.9)

    status_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                          verticalalignment='top', fontsize=11,
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    def get_color_for_province(province, current_assignment, is_current, is_conflict):
        if province in current_assignment:
            return COLOR_HEX.get(current_assignment[province], COLOR_GRAY)
        return COLOR_GRAY

    def update(frame):
        step = steps[frame]
        current_assignment = step['assignment']

        ax.clear()
        ax.set_facecolor('#E8F4F8')
        ax.set_xlim(73, 136)
        ax.set_ylim(15, 55)
        ax.set_title('中国省级行政区四色问题求解过程', fontsize=18, weight='bold',
                    pad=20, color='#2C3E50')
        ax.set_xlabel('经度', fontsize=12)
        ax.set_ylabel('纬度', fontsize=12)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for idx, row in gdf.iterrows():
            province = idx
            if province in PROVINCES:
                color = COLOR_HEX.get(current_assignment.get(province), COLOR_GRAY)
                edge_color = '#2C3E50'
                linewidth = 0.8

                if step['action'] == 'backtrack' and province == step['province']:
                    edge_color = '#E74C3C'
                    linewidth = 2
                elif step['action'] == 'assign' and province == step['province']:
                    edge_color = '#27AE60'
                    linewidth = 2

                gdf.loc[[idx]].plot(ax=ax, color=color, edgecolor=edge_color, linewidth=linewidth)

                centroid = row.geometry.centroid
                short_name = province[:2]
                ax.annotate(short_name, xy=(centroid.x, centroid.y),
                           ha='center', va='center', fontsize=7,
                           color='#2C3E50', weight='bold')

        ax.legend(handles=legend_patches, loc='lower right', fontsize=10,
                 title='四色方案', title_fontsize=12, framealpha=0.9)

        colored_count = len(current_assignment)
        total_count = len(PROVINCES)
        status_text.set_text(f"步骤 {frame + 1}/{len(steps)}\n"
                            f"已着色: {colored_count}/{total_count}\n"
                            f"{step['message']}")

        return []

    anim = animation.FuncAnimation(fig, update, frames=len(steps),
                                   interval=100, blit=True)

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "china_four_color_animation.gif")
    print(f"正在保存动画到 {output_path}...")
    anim.save(output_path, writer=PillowWriter(fps=10))
    print(f"动画已保存至: {output_path}")

    plt.close()

def create_summary_image():
    geojson_data = download_china_map()
    if not geojson_data:
        return

    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    gdf['标准名称'] = gdf['NAME'].apply(standardize_name)

    result, steps = solve_four_color_with_history(PROVINCES, ADJACENCY, COLORS)
    if not result:
        return

    gdf['颜色'] = gdf['标准名称'].map(lambda x: COLOR_HEX.get(result.get(x, "红"), "#E74C3C"))

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))

    key_steps = []
    target_indices = [0, len(steps) // 4, len(steps) // 2, len(steps) - 1]
    for i, step in enumerate(steps):
        if i in target_indices:
            key_steps.append((i, step))

    for ax, (step_idx, step) in zip(axes.flat, key_steps):
        current_assignment = step['assignment']

        ax.set_facecolor('#E8F4F8')
        ax.set_xlim(73, 136)
        ax.set_ylim(15, 55)
        ax.set_title(f"步骤 {step_idx + 1}: {step['message']}", fontsize=12, weight='bold')
        ax.set_xlabel('经度', fontsize=10)
        ax.set_ylabel('纬度', fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        gdf_copy = gdf.copy()
        gdf_copy['显示颜色'] = gdf_copy['标准名称'].map(
            lambda x: COLOR_HEX.get(current_assignment.get(x), COLOR_GRAY)
        )

        for idx, row in gdf_copy.iterrows():
            province = row['标准名称']
            if province in PROVINCES:
                color = row['显示颜色']
                edge_color = '#2C3E50'
                linewidth = 0.8

                if step['action'] == 'backtrack' and province == step['province']:
                    edge_color = '#E74C3C'
                    linewidth = 2
                elif step['action'] == 'assign' and province == step['province']:
                    edge_color = '#27AE60'
                    linewidth = 2

                gdf_copy.loc[[idx]].plot(ax=ax, color=color, edgecolor=edge_color, linewidth=linewidth)

                centroid = row.geometry.centroid
                short_name = province[:2]
                ax.annotate(short_name, xy=(centroid.x, centroid.y),
                           ha='center', va='center', fontsize=5,
                           color='#2C3E50', weight='bold')

        colored = len(current_assignment)
        ax.text(0.02, 0.98, f"已着色: {colored}/{len(PROVINCES)}",
               transform=ax.transAxes, verticalalignment='top',
               fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.suptitle('中国省级行政区四色问题求解过程示意', fontsize=18, weight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "china_four_color_steps.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#F8F9FA')
    print(f"步骤示意图已保存至: {output_path}")
    plt.close()

if __name__ == "__main__":
    print("生成动画...")
    create_step_visualization()

    print("\n生成步骤示意图...")
    create_summary_image()

    print("\n完成！请查看生成的文件：")
    print("  - china_four_color_animation.gif (动画)")
    print("  - china_four_color_steps.png (关键步骤截图)")
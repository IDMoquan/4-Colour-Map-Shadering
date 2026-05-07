import urllib.request
import json
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib.font_manager import FontProperties
import numpy as np
from four_color_solver import PROVINCES, ADJACENCY, COLORS, solve_four_color

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

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

COLOR_HEX = {
    "红": "#E74C3C",
    "绿": "#27AE60",
    "蓝": "#3498DB",
    "黄": "#F1C40F"
}

def download_china_map():
    cache_path = os.path.join(os.path.dirname(__file__), "china_provinces.json")
    if os.path.exists(cache_path):
        print("从缓存加载地图数据...")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    print("下载中国省份地图数据...")
    try:
        with urllib.request.urlopen(CHINA_PROVINCES_GEOJSON_URL, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print("地图数据下载完成并已缓存")
        return data
    except Exception as e:
        print(f"下载失败: {e}")
        return None

def standardize_name(name):
    return PROVINCE_NAME_MAPPING.get(name, name)

def visualize_china_map():
    geojson_data = download_china_map()
    if not geojson_data:
        print("无法获取地图数据")
        return

    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    gdf['标准名称'] = gdf['NAME'].apply(standardize_name)

    solution = solve_four_color(PROVINCES, ADJACENCY, COLORS)
    if not solution:
        print("无法求解四色问题")
        return

    gdf['颜色'] = gdf['标准名称'].map(lambda x: COLOR_HEX.get(solution.get(x, "红"), "#E74C3C"))

    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#E8F4F8')

    gdf.plot(ax=ax, color=gdf['颜色'], edgecolor='#2C3E50', linewidth=0.8)

    for idx, row in gdf.iterrows():
        centroid = row.geometry.centroid
        short_name = row['标准名称'][:2]
        ax.annotate(short_name, xy=(centroid.x, centroid.y),
                   ha='center', va='center', fontsize=7,
                   fontproperties=None, color='#2C3E50', weight='bold')

    legend_patches = [mpatches.Patch(color=color, label=name)
                     for name, color in COLOR_HEX.items()]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=10,
             title='四色方案', title_fontsize=12, framealpha=0.9)

    ax.set_title('中国省级行政区四色问题可视化', fontsize=18, weight='bold',
                pad=20, color='#2C3E50')
    ax.set_xlabel('经度', fontsize=12)
    ax.set_ylabel('纬度', fontsize=12)
    ax.set_xlim(73, 136)
    ax.set_ylim(15, 55)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "china_four_color_map.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
               facecolor=fig.get_facecolor())
    print(f"地图已保存至: {output_path}")

    plt.show()

if __name__ == "__main__":
    visualize_china_map()
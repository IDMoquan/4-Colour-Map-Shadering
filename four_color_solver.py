PROVINCES = [
    "北京", "天津", "河北", "山西", "内蒙古",
    "辽宁", "吉林", "黑龙江", "上海", "江苏",
    "浙江", "安徽", "福建", "江西", "山东",
    "河南", "湖北", "湖南", "广东", "广西",
    "海南", "重庆", "四川", "贵州", "云南",
    "西藏", "陕西", "甘肃", "青海", "宁夏",
    "新疆", "香港", "澳门", "台湾"
]

ADJACENCY = {
    "北京": ["河北", "天津"],
    "天津": ["北京", "河北"],
    "河北": ["北京", "天津", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "山东", "河南"],
    "山西": ["河北", "内蒙古", "陕西", "河南"],
    "内蒙古": ["黑龙江", "吉林", "辽宁", "河北", "山西", "陕西", "甘肃", "宁夏", "新疆"],
    "辽宁": ["吉林", "内蒙古", "河北"],
    "吉林": ["黑龙江", "辽宁", "内蒙古"],
    "黑龙江": ["吉林", "内蒙古"],
    "上海": ["江苏", "浙江"],
    "江苏": ["上海", "浙江", "安徽", "山东"],
    "浙江": ["上海", "江苏", "安徽", "福建", "江西"],
    "安徽": ["江苏", "浙江", "江西", "湖北", "河南", "山东"],
    "福建": ["浙江", "江西", "广东"],
    "江西": ["浙江", "安徽", "福建", "广东", "湖南", "湖北"],
    "山东": ["江苏", "安徽", "河南", "河北"],
    "河南": ["山东", "安徽", "湖北", "陕西", "山西", "河北"],
    "湖北": ["河南", "安徽", "江西", "湖南", "重庆", "陕西"],
    "湖南": ["湖北", "江西", "广东", "广西", "贵州", "重庆"],
    "广东": ["湖南", "江西", "福建", "香港", "澳门", "广西"],
    "广西": ["广东", "湖南", "贵州", "云南", "越南"],
    "海南": ["广东"],
    "重庆": ["湖北", "湖南", "贵州", "四川", "陕西"],
    "四川": ["重庆", "贵州", "云南", "西藏", "青海", "甘肃", "陕西"],
    "贵州": ["重庆", "四川", "云南", "广西", "湖南", "江西"],
    "云南": ["贵州", "四川", "西藏", "广西", "越南", "缅甸", "老挝"],
    "西藏": ["新疆", "青海", "四川", "云南", "印度", "尼泊尔", "不丹", "缅甸"],
    "陕西": ["内蒙古", "山西", "河南", "湖北", "重庆", "四川", "甘肃", "宁夏"],
    "甘肃": ["内蒙古", "新疆", "青海", "四川", "陕西", "宁夏"],
    "青海": ["西藏", "新疆", "甘肃", "四川", "陕西"],
    "宁夏": ["内蒙古", "陕西", "甘肃"],
    "新疆": ["内蒙古", "甘肃", "青海", "西藏", "哈萨克斯坦", "吉尔吉斯斯坦", "塔吉克斯坦", "巴基斯坦", "阿富汗", "蒙古", "印度", "俄罗斯"],
    "香港": ["广东", "澳门"],
    "澳门": ["广东", "香港"],
    "台湾": ["菲律宾", "日本", "钓鱼岛"],
}

COLORS = ["红", "绿", "蓝", "黄"]

COLOR_HEX = {
    "红": "#E74C3C",
    "绿": "#27AE60",
    "蓝": "#3498DB",
    "黄": "#F1C40F"
}

COLOR_GRAY = "#D3D3D3"

def is_safe(province, color, assignment, adjacency):
    for neighbor in adjacency[province]:
        if neighbor in assignment and assignment[neighbor] == color:
            return False
    return True

def solve_four_color_with_history(province_list, adjacency, colors):
    steps = []

    def backtrack(assignment):
        if len(assignment) == len(province_list):
            return dict(assignment)

        unassigned = [p for p in province_list if p not in assignment]
        province = unassigned[0]

        for color in colors:
            if is_safe(province, color, assignment, adjacency):
                assignment[province] = color
                steps.append({
                    "action": "assign",
                    "province": province,
                    "color": color,
                    "assignment": dict(assignment),
                    "message": f"为 {province} 涂上 {color} 色"
                })

                result = backtrack(assignment)
                if result is not None:
                    return result

                assignment.pop(province)
                steps.append({
                    "action": "backtrack",
                    "province": province,
                    "color": color,
                    "assignment": dict(assignment),
                    "message": f"回溯：{province} 的 {color} 色方案失败，尝试其他颜色"
                })

        return None

    result = backtrack({})
    return result, steps

def main():
    print("=" * 50)
    print("中国省级行政区四色问题求解器")
    print("=" * 50)

    result, steps = solve_four_color_with_history(PROVINCES, ADJACENCY, COLORS)

    if result:
        print(f"\n求解成功！共进行 {len(steps)} 步计算。")
        print("\n着色方案：\n")

        color_map = {}
        for province, color in result.items():
            if color not in color_map:
                color_map[color] = []
            color_map[color].append(province)

        for color, provinces in sorted(color_map.items()):
            print(f"【{color}】: {', '.join(provinces)}")

        print(f"\n共使用 {len(color_map)} 种颜色，为 {len(PROVINCES)} 个省级行政区着色。")
    else:
        print("求解失败！")

    return result, steps

if __name__ == "__main__":
    result, steps = main()
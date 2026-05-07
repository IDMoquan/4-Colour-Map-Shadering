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
    "内蒙古": ["黑龙江", "吉林", "辽宁", "河北", "山西", "陕西", "甘肃", "宁夏"],
    "陕西": ["内蒙古", "山西", "河南", "湖北", "重庆", "四川", "甘肃", "宁夏"],
    "河北": ["北京", "天津", "山西", "内蒙古", "辽宁", "山东", "河南"],
    "四川": ["重庆", "贵州", "云南", "西藏", "青海", "甘肃", "陕西"],
    "甘肃": ["内蒙古", "新疆", "青海", "四川", "陕西", "宁夏"],
    "河南": ["山东", "安徽", "湖北", "陕西", "山西", "河北"],
    "湖北": ["河南", "安徽", "江西", "湖南", "重庆", "陕西"],
    "湖南": ["湖北", "江西", "广东", "广西", "贵州", "重庆"],
    "广东": ["湖南", "江西", "福建", "香港", "澳门", "广西"],
    "江西": ["浙江", "安徽", "福建", "广东", "湖南", "湖北"],
    "浙江": ["上海", "江苏", "安徽", "福建", "江西"],
    "重庆": ["湖北", "湖南", "贵州", "四川", "陕西"],
    "贵州": ["重庆", "四川", "云南", "广西", "湖南"],
    "安徽": ["江苏", "浙江", "江西", "湖北", "河南"],
    "山西": ["河北", "内蒙古", "陕西", "河南"],
    "江苏": ["上海", "浙江", "安徽", "山东"],
    "云南": ["贵州", "四川", "西藏", "广西"],
    "西藏": ["新疆", "青海", "四川", "云南"],
    "青海": ["西藏", "新疆", "甘肃", "四川"],
    "广西": ["广东", "湖南", "贵州", "云南"],
    "吉林": ["黑龙江", "辽宁", "内蒙古"],
    "辽宁": ["吉林", "内蒙古", "河北"],
    "宁夏": ["内蒙古", "陕西", "甘肃"],
    "山东": ["江苏", "河南", "河北"],
    "福建": ["浙江", "江西", "广东"],
    "新疆": ["甘肃", "青海", "西藏"],
    "黑龙江": ["吉林", "内蒙古"],
    "北京": ["河北", "天津"],
    "天津": ["北京", "河北"],
    "上海": ["江苏", "浙江"],
    "香港": ["广东", "澳门"],
    "澳门": ["广东", "香港"],
    "台湾": ["福建"],
    "海南": ["广东"],
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
    province_set = set(province_list)
    num_colors = len(colors)
    
    valid_adjacency = {}
    for p in province_list:
        valid_adjacency[p] = [n for n in adjacency[p] if n in province_set]

    sorted_provinces = sorted(province_list, key=lambda x: len(valid_adjacency[x]), reverse=True)
    province_to_idx = {p: i for i, p in enumerate(sorted_provinces)}

    def get_available_colors_bitmask(province, color_array):
        mask = (1 << num_colors) - 1
        for neighbor in valid_adjacency[province]:
            idx = province_to_idx[neighbor]
            if color_array[idx] != -1:
                mask &= ~(1 << color_array[idx])
        return mask

    def count_bits(mask):
        count = 0
        while mask:
            count += mask & 1
            mask >>= 1
        return count

    def select_next_province_mrv(color_array):
        mrv_idx = -1
        min_options = float('inf')
        max_degree = -1
        for i, p in enumerate(sorted_provinces):
            if color_array[i] == -1:
                mask = get_available_colors_bitmask(p, color_array)
                options = count_bits(mask)
                degree = len(valid_adjacency[p])
                if options < min_options or (options == min_options and degree > max_degree):
                    min_options = options
                    max_degree = degree
                    mrv_idx = i
                if min_options == 1:
                    break
        return mrv_idx

    def forward_check(idx, color_idx, color_array):
        color_array[idx] = color_idx
        for neighbor in valid_adjacency[sorted_provinces[idx]]:
            n_idx = province_to_idx[neighbor]
            if color_array[n_idx] == -1:
                mask = get_available_colors_bitmask(neighbor, color_array)
                if mask == 0:
                    color_array[idx] = -1
                    return False
        return True

    def get_color_order(mask, color_array):
        color_counts = [0] * num_colors
        for i in range(len(color_array)):
            if color_array[i] != -1:
                color_counts[color_array[i]] += 1

        order = []
        temp_mask = mask
        while temp_mask:
            lsb = temp_mask & -temp_mask
            c_idx = (lsb - 1).bit_length()
            order.append((color_counts[c_idx], c_idx))
            temp_mask ^= lsb
        order.sort(key=lambda x: x[0])
        return [c[1] for c in order]

    color_array = [-1] * len(sorted_provinces)
    coloring_order = []
    
    def backtrack():
        if -1 not in color_array:
            result = {sorted_provinces[i]: colors[color_array[i]] for i in range(len(sorted_provinces))}
            return result

        idx = select_next_province_mrv(color_array)
        if idx == -1:
            return None
            
        province = sorted_provinces[idx]
        mask = get_available_colors_bitmask(province, color_array)
        if mask == 0:
            return None

        color_order = get_color_order(mask, color_array)

        for color_idx in color_order:
            color = colors[color_idx]
            
            if forward_check(idx, color_idx, color_array):
                coloring_order.append((province, color))
                steps.append({
                    "action": "assign",
                    "province": province,
                    "color": color,
                    "assignment": {sorted_provinces[i]: colors[color_array[i]] for i in range(len(color_array)) if color_array[i] != -1},
                    "message": f"为 {province} 涂上 {color} 色"
                })
                result = backtrack()
                if result is not None:
                    return result

            color_array[idx] = -1
            steps.append({
                "action": "backtrack",
                "province": province,
                "color": color,
                "assignment": {sorted_provinces[i]: colors[color_array[i]] for i in range(len(color_array)) if color_array[i] != -1},
                "message": f"回溯：{province} 的 {color} 色方案失败，尝试其他颜色"
            })

        return None

    result = backtrack()
    
    initial_step = {
        "action": "initial",
        "province": "",
        "color": "",
        "assignment": {},
        "message": "初始状态：所有省份待着色"
    }
    steps.insert(0, initial_step)
    
    return result, steps, coloring_order

def main():
    print("=" * 50)
    print("中国省级行政区四色问题求解器")
    print("=" * 50)

    result, steps, coloring_order = solve_four_color_with_history(PROVINCES, ADJACENCY, COLORS)

    if result:
        print(f"\n求解成功！共进行 {len(steps)} 步计算。")
        
        print("\n填色顺序：")
        print("-" * 40)
        for i, (province, color) in enumerate(coloring_order, 1):
            print(f"{i:2d}. {province:4s} → {color}")
        print("-" * 40)
        
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
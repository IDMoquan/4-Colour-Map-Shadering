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
        if neighbor in PROVINCES and neighbor in assignment and assignment[neighbor] == color:
            return False
    return True

def solve_four_color_with_history(province_list, adjacency, colors):
    steps = []
    conflict_set = {}

    def get_remaining_values(assignment):
        remaining = {}
        for province in province_list:
            if province not in assignment:
                available_colors = []
                for color in colors:
                    if is_safe(province, color, assignment, adjacency):
                        available_colors.append(color)
                remaining[province] = available_colors
        return remaining

    def select_variable_mrv(assignment):
        remaining = get_remaining_values(assignment)
        min_count = float('inf')
        selected = None
        
        for province, available_colors in remaining.items():
            if len(available_colors) < min_count:
                min_count = len(available_colors)
                selected = province
            elif len(available_colors) == min_count:
                if len(adjacency[province]) > len(adjacency[selected]):
                    selected = province
        
        return selected

    def select_variable_degree(assignment):
        """度启发式：选择对其它变量约束数最大的变量"""
        unassigned = [p for p in province_list if p not in assignment]
        max_degree = -1
        selected = None
        
        for province in unassigned:
            degree = 0
            for neighbor in adjacency[province]:
                if neighbor not in assignment:
                    degree += 1
            
            if degree > max_degree:
                max_degree = degree
                selected = province
            elif degree == max_degree:
                remaining = get_remaining_values(assignment)
                if len(remaining[province]) < len(remaining[selected]):
                    selected = province
        
        return selected

    def order_domain_values(province, assignment):
        """最少约束值启发式：选择对邻居变量可选值影响最少的颜色"""
        remaining = get_remaining_values(assignment)
        color_scores = []
        
        for color in colors:
            if not is_safe(province, color, assignment, adjacency):
                continue
                
            impact = 0
            for neighbor in adjacency[province]:
                if neighbor in province_list and neighbor not in assignment:
                    neighbor_colors = remaining[neighbor]
                    if color in neighbor_colors:
                        impact += 1
            
            color_scores.append((color, impact))
        
        color_scores.sort(key=lambda x: x[1])
        return [color for color, _ in color_scores]

    def update_conflict_set(conflict_province, current_province):
        """更新冲突集"""
        if current_province not in conflict_set:
            conflict_set[current_province] = set()
        conflict_set[current_province].add(conflict_province)

    def backtrack_with_cbj(assignment, level=0):
        """带冲突导向后向跳转的回溯算法"""
        if len(assignment) == len(province_list):
            return dict(assignment)

        province = select_variable_mrv(assignment)
        ordered_colors = order_domain_values(province, assignment)
        
        current_conflicts = set()
        
        for color in ordered_colors:
            if is_safe(province, color, assignment, adjacency):
                assignment[province] = color
                steps.append({
                    "action": "assign",
                    "province": province,
                    "color": color,
                    "assignment": dict(assignment),
                    "message": f"为 {province} 涂上 {color} 色（使用优化启发式）"
                })

                result = backtrack_with_cbj(assignment, level + 1)
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

                for conflict_province in current_conflicts:
                    update_conflict_set(conflict_province, province)
                current_conflicts.clear()
            else:

                for neighbor in adjacency[province]:
                    if neighbor in assignment and assignment[neighbor] == color:
                        current_conflicts.add(neighbor)

        if current_conflicts:
            latest_conflict = max(current_conflicts, 
                                key=lambda p: list(assignment.keys()).index(p) if p in assignment else -1)
            if latest_conflict in assignment:
                return None 

        return None

    result = backtrack_with_cbj({})
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
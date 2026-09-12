"""
五城十味绘图数据 - 占位版本
后续可替换为高精度插画数据
"""

from ...config import rgb, make_style, linear_gradient, radial_gradient


# 通用盘子
def plate_drawing(cx, cy, r):
    return [
        ['E', [cx, cy - 0.02, r * 1.2, r * 0.3], {'fill': rgb(180, 180, 180)}],  # 阴影
        ['C', [cx, cy, r], {'fill': rgb(240, 240, 240), 'stroke': rgb(200, 200, 200), 'stroke_width': 2}],
        ['C', [cx, cy, r * 0.9], {'stroke': rgb(220, 220, 220), 'stroke_width': 1}],
    ]


# 北京烤鸭
ROAST_DUCK = [
    *plate_drawing(0.5, 0.45, 0.18),
    # 鸭身
    ['E', [0.5, 0.45, 0.15, 0.1], {'fill': rgb(139, 69, 19)}],
    ['E', [0.5, 0.47, 0.13, 0.08], {'fill': rgb(160, 82, 45)}],
    # 高光
    ['E', [0.45, 0.48, 0.04, 0.02], {'fill': rgb(205, 133, 63)}],
    # 切片线条
    ['L', [[0.42, 0.42], [0.42, 0.52]], {'stroke': rgb(100, 50, 20), 'stroke_width': 1}],
    ['L', [[0.47, 0.41], [0.47, 0.53]], {'stroke': rgb(100, 50, 20), 'stroke_width': 1}],
    ['L', [[0.52, 0.41], [0.52, 0.53]], {'stroke': rgb(100, 50, 20), 'stroke_width': 1}],
    ['L', [[0.57, 0.42], [0.57, 0.52]], {'stroke': rgb(100, 50, 20), 'stroke_width': 1}],
]


# 月饼
MOONCAKE = [
    *plate_drawing(0.5, 0.45, 0.15),
    # 月饼主体
    ['C', [0.5, 0.45, 0.1], {'fill': rgb(218, 165, 32)}],
    ['C', [0.5, 0.45, 0.09], {'fill': rgb(205, 133, 0)}],
    # 花纹
    ['RG', [0.5, 0.45, 0.06, 0.08], {'stroke': rgb(184, 134, 11), 'stroke_width': 1}],
    ['C', [0.5, 0.45, 0.04], {'fill': rgb(255, 215, 0)}],
]


# 包子
BAOZI = [
    *plate_drawing(0.5, 0.45, 0.15),
    # 包子主体
    ['C', [0.5, 0.45, 0.1], {'fill': rgb(255, 250, 240)}],
    # 褶子
    ['A', [0.5, 0.45, 0.08, 0, 360], {'stroke': rgb(220, 210, 200), 'stroke_width': 1}],
    # 顶部
    ['C', [0.5, 0.48, 0.02], {'fill': rgb(240, 230, 220)}],
    # 蒸汽
    ['A', [0.45, 0.55, 0.02, 0, 180], {'stroke': rgb(200, 200, 200), 'stroke_width': 1}],
    ['A', [0.5, 0.57, 0.02, 0, 180], {'stroke': rgb(200, 200, 200), 'stroke_width': 1}],
    ['A', [0.55, 0.55, 0.02, 0, 180], {'stroke': rgb(200, 200, 200), 'stroke_width': 1}],
]


# 麻花
MAHUA = [
    *plate_drawing(0.5, 0.45, 0.18),
    # 麻花主体 - 交叉的条
    ['B', [[0.35, 0.4], [0.45, 0.5], [0.55, 0.4], [0.65, 0.5]], {'stroke': rgb(205, 133, 0), 'stroke_width': 8}],
    ['B', [[0.35, 0.5], [0.45, 0.4], [0.55, 0.5], [0.65, 0.4]], {'stroke': rgb(184, 134, 11), 'stroke_width': 8}],
    # 芝麻点
    ['P', [0.4, 0.45, 2], {'fill': rgb(255, 255, 200)}],
    ['P', [0.5, 0.43, 2], {'fill': rgb(255, 255, 200)}],
    ['P', [0.6, 0.47, 2], {'fill': rgb(255, 255, 200)}],
]


# 狮子头
LION_HEAD = [
    *plate_drawing(0.5, 0.45, 0.18),
    # 汤汁
    ['E', [0.5, 0.45, 0.15, 0.1], {'fill': rgb(255, 245, 220)}],
    # 狮子头
    ['C', [0.5, 0.45, 0.08], {'fill': rgb(160, 82, 45)}],
    ['C', [0.5, 0.45, 0.07], {'fill': rgb(139, 69, 19)}],
    # 纹理
    ['P', [0.47, 0.43, 2], {'fill': rgb(100, 50, 20)}],
    ['P', [0.52, 0.46, 2], {'fill': rgb(100, 50, 20)}],
    ['P', [0.48, 0.48, 2], {'fill': rgb(100, 50, 20)}],
    # 青菜
    ['E', [0.38, 0.45, 0.03, 0.02], {'fill': rgb(34, 139, 34)}],
    ['E', [0.62, 0.45, 0.03, 0.02], {'fill': rgb(34, 139, 34)}],
]


# 汤包
SOUP_DUMPLING = [
    *plate_drawing(0.5, 0.45, 0.15),
    # 汤包主体
    ['C', [0.5, 0.45, 0.08], {'fill': rgb(255, 250, 240)}],
    # 褶子顶部
    ['A', [0.5, 0.45, 0.06, 0, 360], {'stroke': rgb(220, 210, 200), 'stroke_width': 1}],
    ['C', [0.5, 0.47, 0.015], {'fill': rgb(200, 180, 160)}],
    # 醋碟
    ['C', [0.65, 0.5, 0.04], {'fill': rgb(240, 240, 240), 'stroke': rgb(200, 200, 200), 'stroke_width': 1}],
    ['C', [0.65, 0.5, 0.03], {'fill': rgb(139, 69, 19)}],
]


# 桂花糕
OSMANTHUS_CAKE = [
    *plate_drawing(0.5, 0.45, 0.18),
    # 糕体
    ['R', [0.4, 0.4, 0.2, 0.1], {'fill': rgb(255, 245, 220)}],
    ['R', [0.41, 0.41, 0.18, 0.08], {'fill': rgb(255, 235, 205)}],
    # 桂花点缀
    ['P', [0.43, 0.43, 3], {'fill': rgb(255, 165, 0)}],
    ['P', [0.48, 0.45, 3], {'fill': rgb(255, 140, 0)}],
    ['P', [0.53, 0.42, 3], {'fill': rgb(255, 165, 0)}],
    ['P', [0.57, 0.46, 3], {'fill': rgb(255, 140, 0)}],
]


# 松鼠桂鱼
SQUIRREL_FISH = [
    *plate_drawing(0.5, 0.45, 0.2),
    # 鱼身
    ['E', [0.5, 0.45, 0.15, 0.08], {'fill': rgb(205, 133, 0)}],
    # 菱形刀花
    ['L', [[0.4, 0.42], [0.6, 0.42]], {'stroke': rgb(184, 134, 11), 'stroke_width': 1}],
    ['L', [[0.4, 0.45], [0.6, 0.45]], {'stroke': rgb(184, 134, 11), 'stroke_width': 1}],
    ['L', [[0.4, 0.48], [0.6, 0.48]], {'stroke': rgb(184, 134, 11), 'stroke_width': 1}],
    # 酱汁
    ['E', [0.5, 0.45, 0.12, 0.06], {'fill': rgb(220, 20, 60)}],
    # 松仁
    ['P', [0.45, 0.5, 2], {'fill': rgb(255, 228, 196)}],
    ['P', [0.5, 0.51, 2], {'fill': rgb(255, 228, 196)}],
    ['P', [0.55, 0.5, 2], {'fill': rgb(255, 228, 196)}],
]


# 龙井茶
LONGJING_TEA = [
    *plate_drawing(0.5, 0.45, 0.12),
    # 茶杯
    ['R', [0.42, 0.4, 0.16, 0.12], {'fill': rgb(240, 240, 240), 'stroke': rgb(200, 200, 200), 'stroke_width': 2}],
    # 茶水
    ['R', [0.44, 0.42, 0.12, 0.08], {'fill': rgb(144, 238, 144)}],
    # 茶叶
    ['L', [[0.47, 0.44], [0.47, 0.48]], {'stroke': rgb(34, 139, 34), 'stroke_width': 1}],
    ['L', [[0.5, 0.43], [0.5, 0.47]], {'stroke': rgb(34, 139, 34), 'stroke_width': 1}],
    ['L', [[0.53, 0.45], [0.53, 0.49]], {'stroke': rgb(34, 139, 34), 'stroke_width': 1}],
    # 茶汽
    ['A', [0.47, 0.52, 0.02, 0, 180], {'stroke': rgb(200, 200, 200), 'stroke_width': 1}],
    ['A', [0.53, 0.53, 0.02, 0, 180], {'stroke': rgb(200, 200, 200), 'stroke_width': 1}],
]


# 西湖醋鱼
WEST_LAKE_FISH = [
    *plate_drawing(0.5, 0.45, 0.2),
    # 鱼身
    ['E', [0.5, 0.45, 0.15, 0.07], {'fill': rgb(160, 82, 45)}],
    # 鱼尾
    ['G', [[0.65, 0.45], [0.7, 0.42], [0.7, 0.48]], {'fill': rgb(139, 69, 19)}],
    # 酱汁
    ['E', [0.5, 0.45, 0.12, 0.05], {'fill': rgb(139, 0, 0)}],
    # 姜丝
    ['L', [[0.45, 0.44], [0.48, 0.44]], {'stroke': rgb(255, 255, 0), 'stroke_width': 1}],
    ['L', [[0.5, 0.46], [0.53, 0.46]], {'stroke': rgb(255, 255, 0), 'stroke_width': 1}],
    # 葱丝
    ['L', [[0.47, 0.47], [0.5, 0.47]], {'stroke': rgb(0, 255, 0), 'stroke_width': 1}],
]


# 食物绘图数据映射
FOOD_DRAWINGS = {
    'beijing_roast_duck': ROAST_DUCK,
    'beijing_mooncake': MOONCAKE,
    'tianjin_baozi': BAOZI,
    'tianjin_mahua': MAHUA,
    'yangzhou_lion_head': LION_HEAD,
    'yangzhou_soup_dumpling': SOUP_DUMPLING,
    'suzhou_osmanthus_cake': OSMANTHUS_CAKE,
    'suzhou_squirrel_fish': SQUIRREL_FISH,
    'hangzhou_longjing_tea': LONGJING_TEA,
    'hangzhou_west_lake_fish': WEST_LAKE_FISH,
}


def get_food_drawing(city_id: str, food_id: str) -> list:
    """获取食物的绘图数据"""
    key = f"{city_id}_{food_id}"
    return FOOD_DRAWINGS.get(key, [])

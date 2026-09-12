"""
五城二十味矢量绘图数据
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


# 二期新增菜品共用一套克制的矢量餐具语言，但保留各自轮廓与配色。
NOODLE_BOWL = [
    *plate_drawing(0.5, 0.40, 0.18),
    ['G', [[.34,.48],[.66,.48],[.60,.34],[.40,.34]],
     {'fill': rgb(238, 231, 208), 'stroke': rgb(120, 91, 61), 'stroke_width': 2}],
    ['E', [.50,.48,.16,.045], {'fill': rgb(132, 75, 34)}],
    ['B', [[.39,.49],[.45,.45],[.54,.52],[.62,.47]], {'stroke': rgb(238, 195, 92), 'stroke_width': 3}],
    ['L', [[.42,.54],[.64,.62]], {'stroke': rgb(103, 65, 39), 'stroke_width': 2}],
]

HOTPOT = [
    *plate_drawing(0.5, 0.40, 0.19),
    ['E', [.50,.45,.17,.10], {'fill': rgb(151, 65, 42), 'stroke': rgb(91, 50, 36), 'stroke_width': 2}],
    ['E', [.50,.48,.145,.066], {'fill': rgb(213, 114, 62)}],
    ['R', [.47,.47,.06,.13], {'fill': rgb(176, 147, 92), 'stroke': rgb(93, 67, 45), 'stroke_width': 1}],
    ['B', [[.41,.55],[.39,.59],[.42,.63],[.40,.67]], {'stroke': rgb(204, 199, 182), 'stroke_width': 2}],
    ['B', [[.58,.55],[.56,.59],[.59,.63],[.57,.67]], {'stroke': rgb(204, 199, 182), 'stroke_width': 2}],
]

STEW_BOWL = [
    *plate_drawing(0.5, 0.40, 0.18),
    ['G', [[.34,.48],[.66,.48],[.60,.34],[.40,.34]], {'fill': rgb(225, 211, 181), 'stroke': rgb(112, 77, 49), 'stroke_width': 2}],
    ['E', [.50,.48,.16,.05], {'fill': rgb(105, 59, 34)}],
    ['C', [.44,.49,.035], {'fill': rgb(170, 101, 55)}],
    ['C', [.53,.47,.040], {'fill': rgb(189, 125, 64)}],
    ['R', [.56,.47,.055,.025], {'fill': rgb(218, 187, 124)}],
]

JIANBING = [
    *plate_drawing(0.5, 0.43, 0.19),
    ['G', [[.34,.39],[.61,.35],[.67,.50],[.40,.55]], {'fill': rgb(222, 166, 61), 'stroke': rgb(133, 81, 33), 'stroke_width': 2}],
    ['G', [[.43,.39],[.60,.37],[.64,.47],[.47,.50]], {'fill': rgb(235, 205, 109)}],
    ['L', [[.37,.47],[.64,.42]], {'stroke': rgb(132, 52, 32), 'stroke_width': 2}],
    ['L', [[.45,.52],[.57,.38]], {'stroke': rgb(65, 126, 69), 'stroke_width': 2}],
]

TOFU_SILK = [
    *plate_drawing(0.5, 0.41, 0.18),
    ['E', [.50,.45,.16,.095], {'fill': rgb(229, 199, 121), 'stroke': rgb(126, 89, 49), 'stroke_width': 2}],
    *[['L', [[x,.40],[x+.035,.51]], {'stroke': rgb(250, 239, 194), 'stroke_width': 2}]
      for x in (.39,.43,.47,.51,.55,.59)],
    ['E', [.45,.50,.025,.012], {'fill': rgb(197, 80, 47)}],
    ['E', [.57,.43,.028,.012], {'fill': rgb(72, 135, 71)}],
]

FRIED_RICE = [
    *plate_drawing(0.5, 0.42, 0.18),
    ['E', [.50,.45,.145,.09], {'fill': rgb(239, 190, 73)}],
    *[['C', [x,y,.012], {'fill': color}] for x, y, color in (
        (.43,.46,rgb(91,145,74)), (.48,.50,rgb(213,91,54)),
        (.54,.44,rgb(242,221,132)), (.59,.49,rgb(91,145,74)),
        (.49,.41,rgb(213,91,54)),
    )],
]

EEL_PASTE = [
    *plate_drawing(0.5, 0.42, 0.18),
    ['E', [.50,.45,.15,.085], {'fill': rgb(97, 50, 31)}],
    ['B', [[.39,.44],[.45,.53],[.53,.37],[.62,.48]], {'stroke': rgb(185, 103, 47), 'stroke_width': 6}],
    ['L', [[.47,.55],[.54,.37]], {'stroke': rgb(244, 224, 154), 'stroke_width': 2}],
]

RICE_CAKE = [
    *plate_drawing(0.5, 0.42, 0.18),
    ['R', [.38,.39,.11,.10], {'fill': rgb(244, 226, 210), 'stroke': rgb(185, 133, 95), 'stroke_width': 1}],
    ['R', [.51,.42,.11,.10], {'fill': rgb(225, 206, 173), 'stroke': rgb(185, 133, 95), 'stroke_width': 1}],
    ['C', [.43,.45,.018], {'fill': rgb(196, 78, 70)}],
    ['C', [.56,.48,.018], {'fill': rgb(107, 145, 76)}],
]

DONGPO_PORK = [
    *plate_drawing(0.5, 0.42, 0.18),
    ['R', [.39,.36,.22,.16], {'fill': rgb(126, 48, 31), 'stroke': rgb(83, 42, 30), 'stroke_width': 2}],
    ['R', [.40,.44,.20,.065], {'fill': rgb(188, 75, 43)}],
    ['R', [.40,.405,.20,.035], {'fill': rgb(229, 157, 94)}],
    ['E', [.46,.49,.045,.015], {'fill': rgb(236, 174, 111)}],
]

LONGJING_SHRIMP = [
    *plate_drawing(0.5, 0.42, 0.19),
    *[['A', [x,y,.035,20,300], {'stroke': rgb(239, 167, 153), 'stroke_width': 5}]
      for x, y in ((.40,.43),(.47,.49),(.54,.42),(.60,.48))],
    ['L', [[.42,.51],[.45,.55]], {'stroke': rgb(62, 132, 67), 'stroke_width': 2}],
    ['L', [[.55,.51],[.58,.56]], {'stroke': rgb(62, 132, 67), 'stroke_width': 2}],
]


# 食物绘图数据映射
FOOD_DRAWINGS = {
    'beijing_roast_duck': ROAST_DUCK,
    'beijing_mutton_hotpot': HOTPOT,
    'beijing_zhajiang_noodles': NOODLE_BOWL,
    'beijing_luzhu': STEW_BOWL,
    'tianjin_jianbing': JIANBING,
    'tianjin_baozi': BAOZI,
    'tianjin_mahua': MAHUA,
    'tianjin_guobacai': STEW_BOWL,
    'yangzhou_lion_head': LION_HEAD,
    'yangzhou_boiled_shredded_tofu': TOFU_SILK,
    'yangzhou_soup_dumpling': SOUP_DUMPLING,
    'yangzhou_fried_rice': FRIED_RICE,
    'suzhou_squirrel_fish': SQUIRREL_FISH,
    'suzhou_suzhou_noodles': NOODLE_BOWL,
    'suzhou_eel_paste': EEL_PASTE,
    'suzhou_rice_cake': RICE_CAKE,
    'hangzhou_west_lake_fish': WEST_LAKE_FISH,
    'hangzhou_dongpo_pork': DONGPO_PORK,
    'hangzhou_longjing_shrimp': LONGJING_SHRIMP,
    'hangzhou_pianerchuan': NOODLE_BOWL,
}


def get_food_drawing(city_id: str, food_id: str) -> list:
    """获取食物的绘图数据"""
    key = f"{city_id}_{food_id}"
    return FOOD_DRAWINGS.get(key, [])

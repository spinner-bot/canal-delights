"""
五城十味内容数据
"""

from ..config import rgb, linear_gradient, radial_gradient, make_style


# 城市定义
CITIES = [
    {
        'id': 'beijing',
        'name': '北京',
        'theme': rgb(201, 48, 44),  # 朱砂红
        'season': '冬/秋',
        'foods': [
            {
                'id': 'roast_duck',
                'name': '北京烤鸭',
                'season': '秋冬',
                'ingredients': ['鸭', '甜面酱', '葱丝', '黄瓜'],
                'story': '京城名馔，百年传承',
            },
            {
                'id': 'mooncake',
                'name': '中秋月饼',
                'season': '秋',
                'ingredients': ['面粉', '莲蓉', '咸蛋黄'],
                'story': '月满中秋，团圆之味',
            },
        ]
    },
    {
        'id': 'tianjin',
        'name': '天津',
        'theme': rgb(139, 69, 19),  # 赭石
        'season': '春/冬',
        'foods': [
            {
                'id': 'baozi',
                'name': '狗不理包子',
                'season': '四季',
                'ingredients': ['面粉', '猪肉', '姜末'],
                'story': '津门老字号，十八道褶',
            },
            {
                'id': 'mahua',
                'name': '十八街麻花',
                'season': '四季',
                'ingredients': ['面粉', '芝麻', '糖'],
                'story': '酥脆香甜，津门一绝',
            },
        ]
    },
    {
        'id': 'yangzhou',
        'name': '扬州',
        'theme': rgb(46, 139, 87),  # 青碧
        'season': '秋/春',
        'foods': [
            {
                'id': 'lion_head',
                'name': '蟹粉狮子头',
                'season': '秋',
                'ingredients': ['猪肉', '蟹粉', '青菜'],
                'story': '淮扬名菜，入口即化',
            },
            {
                'id': 'soup_dumpling',
                'name': '蟹黄汤包',
                'season': '秋',
                'ingredients': ['面粉', '蟹黄', '猪皮冻'],
                'story': '皮薄汤足，鲜美无比',
            },
        ]
    },
    {
        'id': 'suzhou',
        'name': '苏州',
        'theme': rgb(65, 105, 225),  # 靛蓝
        'season': '秋/春',
        'foods': [
            {
                'id': 'osmanthus_cake',
                'name': '桂花糕',
                'season': '秋',
                'ingredients': ['糯米', '桂花', '糖'],
                'story': '桂香四溢，软糯香甜',
            },
            {
                'id': 'squirrel_fish',
                'name': '松鼠桂鱼',
                'season': '春',
                'ingredients': ['桂鱼', '番茄酱', '松仁'],
                'story': '形似松鼠，酸甜可口',
            },
        ]
    },
    {
        'id': 'hangzhou',
        'name': '杭州',
        'theme': rgb(107, 142, 35),  # 茶绿
        'season': '春/夏',
        'foods': [
            {
                'id': 'longjing_tea',
                'name': '龙井茶',
                'season': '春',
                'ingredients': ['龙井茶叶', '西湖水'],
                'story': '色绿香郁，味醇形美',
            },
            {
                'id': 'west_lake_fish',
                'name': '西湖醋鱼',
                'season': '夏',
                'ingredients': ['草鱼', '醋', '姜末'],
                'story': '鲜嫩酸甜，西湖名菜',
            },
        ]
    },
]


def get_city(index: int) -> dict:
    """获取城市数据"""
    return CITIES[index % len(CITIES)]


def get_food(city_index: int, food_index: int) -> dict:
    """获取美食数据"""
    city = get_city(city_index)
    return city['foods'][food_index % len(city['foods'])]


def get_all_cities() -> list:
    """获取所有城市"""
    return CITIES
